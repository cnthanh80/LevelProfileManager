from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.compliance_score import ComplianceScore
from app.models.evidence_document import EvidenceDocument
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.periodic_review import PeriodicReview
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.risk_assessment import RiskAssessment
from app.models.security_requirement import SecurityRequirement
from app.models.user import User

router = APIRouter(prefix="/dashboard/enterprise")


def _dict(rows) -> dict:
    return {str(k): int(v) for k, v in rows if k is not None}


def _avg(value) -> float:
    return round(float(value or 0), 2)


def _profile_evidence_gap_count(db: Session) -> int:
    sub = (
        select(LevelProfile.id)
        .outerjoin(EvidenceDocument, EvidenceDocument.profile_id == LevelProfile.id)
        .group_by(LevelProfile.id)
        .having(func.count(EvidenceDocument.id) == 0)
    )
    return len(db.scalars(sub).all())


@router.get("/overview")
def enterprise_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    today = date.today()
    total_systems = db.scalar(select(func.count(InformationSystem.id))) or 0
    total_profiles = db.scalar(select(func.count(LevelProfile.id))) or 0
    total_documents = db.scalar(select(func.count(EvidenceDocument.id))) or 0

    level_3_or_above = db.scalar(select(func.count(InformationSystem.id)).where(InformationSystem.proposed_level >= 3)) or 0
    approved_profiles = db.scalar(select(func.count(LevelProfile.id)).where(LevelProfile.status.in_(["INTERNALLY_APPROVED", "APPROVAL_DECISION_ISSUED", "COMPLETED"]))) or 0
    review_due_30 = db.scalar(
        select(func.count(PeriodicReview.id)).where(
            PeriodicReview.status != "COMPLETED",
            PeriodicReview.due_date <= today + timedelta(days=30),
        )
    ) or 0
    overdue_reviews = db.scalar(
        select(func.count(PeriodicReview.id)).where(
            PeriodicReview.status != "COMPLETED",
            PeriodicReview.due_date < today,
        )
    ) or 0

    avg_compliance = db.scalar(select(func.avg(ComplianceScore.overall_score)))
    avg_risk = db.scalar(select(func.avg(RiskAssessment.risk_score)))

    mandatory_gap = db.scalar(
        select(func.count(ProfileRequirementAnswer.id))
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(SecurityRequirement.is_mandatory.is_(True), ProfileRequirementAnswer.status == "NON_COMPLIANT")
    ) or 0

    return {
        "total_systems": total_systems,
        "total_profiles": total_profiles,
        "total_documents": total_documents,
        "level_3_or_above": level_3_or_above,
        "approved_profiles": approved_profiles,
        "profiles_missing_evidence": _profile_evidence_gap_count(db),
        "mandatory_gap": mandatory_gap,
        "review_due_30_days": review_due_30,
        "overdue_reviews": overdue_reviews,
        "average_compliance_score": _avg(avg_compliance),
        "average_risk_score": _avg(avg_risk),
        "executive_status": "ATTENTION_REQUIRED" if (mandatory_gap or overdue_reviews) else "NORMAL",
    }


@router.get("/level-matrix")
def level_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    systems_by_level = _dict(
        db.execute(
            select(InformationSystem.proposed_level, func.count(InformationSystem.id))
            .group_by(InformationSystem.proposed_level)
            .order_by(InformationSystem.proposed_level)
        ).all()
    )
    profiles_by_level = _dict(
        db.execute(
            select(LevelProfile.proposed_level, func.count(LevelProfile.id))
            .group_by(LevelProfile.proposed_level)
            .order_by(LevelProfile.proposed_level)
        ).all()
    )
    profile_status_by_level = db.execute(
        select(LevelProfile.proposed_level, LevelProfile.status, func.count(LevelProfile.id))
        .group_by(LevelProfile.proposed_level, LevelProfile.status)
        .order_by(LevelProfile.proposed_level, LevelProfile.status)
    ).all()
    rows = []
    for level in range(1, 6):
        statuses = {r.status: int(r.count) for r in profile_status_by_level if r.proposed_level == level}
        rows.append(
            {
                "level": level,
                "systems": systems_by_level.get(str(level), 0),
                "profiles": profiles_by_level.get(str(level), 0),
                "workflow_statuses": statuses,
            }
        )
    return {"items": rows}


@router.get("/compliance-risk")
def compliance_risk_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = db.execute(
        select(
            LevelProfile.id,
            LevelProfile.profile_code,
            LevelProfile.proposed_level,
            LevelProfile.status,
            ComplianceScore.overall_score,
            ComplianceScore.management_score,
            ComplianceScore.technical_score,
            ComplianceScore.gap_total,
            RiskAssessment.risk_score,
            RiskAssessment.risk_level,
        )
        .outerjoin(ComplianceScore, ComplianceScore.profile_id == LevelProfile.id)
        .outerjoin(RiskAssessment, RiskAssessment.profile_id == LevelProfile.id)
        .order_by(
            case((RiskAssessment.risk_level == "CRITICAL", 1), (RiskAssessment.risk_level == "HIGH", 2), (RiskAssessment.risk_level == "MEDIUM", 3), else_=4),
            ComplianceScore.overall_score.asc().nullslast(),
            LevelProfile.id,
        )
        .limit(100)
    ).all()
    items = [
        {
            "profile_id": r.id,
            "profile_code": r.profile_code,
            "proposed_level": r.proposed_level,
            "status": r.status,
            "overall_score": r.overall_score or 0,
            "management_score": r.management_score or 0,
            "technical_score": r.technical_score or 0,
            "gap_total": r.gap_total or 0,
            "risk_score": r.risk_score or 0,
            "risk_level": r.risk_level or "NOT_ASSESSED",
        }
        for r in rows
    ]
    risk_distribution = _dict(db.execute(select(RiskAssessment.risk_level, func.count(RiskAssessment.id)).group_by(RiskAssessment.risk_level)).all())
    return {"risk_distribution": risk_distribution, "items": items}


@router.get("/action-board")
def action_board(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    today = date.today()
    mandatory_non_compliant = db.execute(
        select(
            ProfileRequirementAnswer.id,
            LevelProfile.profile_code,
            LevelProfile.proposed_level,
            SecurityRequirement.code,
            SecurityRequirement.title,
            ProfileRequirementAnswer.owner,
            ProfileRequirementAnswer.due_date,
        )
        .join(LevelProfile, ProfileRequirementAnswer.profile_id == LevelProfile.id)
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(SecurityRequirement.is_mandatory.is_(True), ProfileRequirementAnswer.status == "NON_COMPLIANT")
        .order_by(ProfileRequirementAnswer.due_date.asc().nullslast(), LevelProfile.proposed_level.desc(), SecurityRequirement.code)
        .limit(50)
    ).all()

    due_reviews = db.execute(
        select(PeriodicReview.id, PeriodicReview.review_code, PeriodicReview.profile_id, PeriodicReview.status, PeriodicReview.due_date)
        .where(PeriodicReview.status != "COMPLETED", PeriodicReview.due_date <= today + timedelta(days=30))
        .order_by(PeriodicReview.due_date.asc())
        .limit(50)
    ).all()

    missing_evidence = db.execute(
        select(LevelProfile.id, LevelProfile.profile_code, LevelProfile.proposed_level, LevelProfile.status)
        .outerjoin(EvidenceDocument, EvidenceDocument.profile_id == LevelProfile.id)
        .group_by(LevelProfile.id, LevelProfile.profile_code, LevelProfile.proposed_level, LevelProfile.status)
        .having(func.count(EvidenceDocument.id) == 0)
        .order_by(LevelProfile.proposed_level.desc(), LevelProfile.profile_code)
        .limit(50)
    ).all()

    return {
        "mandatory_non_compliant": [
            {
                "answer_id": r.id,
                "profile_code": r.profile_code,
                "proposed_level": r.proposed_level,
                "requirement_code": r.code,
                "requirement_title": r.title,
                "owner": r.owner,
                "due_date": r.due_date.isoformat() if r.due_date else None,
            }
            for r in mandatory_non_compliant
        ],
        "due_reviews": [
            {
                "review_id": r.id,
                "review_code": r.review_code,
                "profile_id": r.profile_id,
                "status": r.status,
                "due_date": r.due_date.isoformat(),
            }
            for r in due_reviews
        ],
        "profiles_missing_evidence": [
            {"profile_id": r.id, "profile_code": r.profile_code, "proposed_level": r.proposed_level, "status": r.status}
            for r in missing_evidence
        ],
    }


@router.get("/executive-report")
def executive_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    overview = enterprise_overview(db, current_user)
    matrix = level_matrix(db, current_user)
    compliance_risk = compliance_risk_dashboard(db, current_user)
    action_items = action_board(db, current_user)
    return {
        "overview": overview,
        "level_matrix": matrix["items"],
        "risk_distribution": compliance_risk["risk_distribution"],
        "top_risk_profiles": compliance_risk["items"][:10],
        "action_items": action_items,
    }
