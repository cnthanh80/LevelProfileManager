from __future__ import annotations

from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.assessment_portal import AssessmentCase, AssessmentFeedback
from app.models.compliance_score import ComplianceScore
from app.models.evidence_document import EvidenceDocument
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.periodic_review import PeriodicReview
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.risk_assessment import RiskAssessment
from app.models.risk_register import RiskRegisterItem, SlaPolicy
from app.models.security_requirement import SecurityRequirement
from app.models.user import User

router = APIRouter(prefix="/dashboard/executive")


def _count(db: Session, stmt) -> int:
    return int(db.scalar(stmt) or 0)


def _avg(db: Session, stmt) -> float:
    return round(float(db.scalar(stmt) or 0), 2)


def _dict(rows) -> dict:
    return {str(k): int(v) for k, v in rows if k is not None}


def _risk_color(level: str) -> str:
    return {
        "CRITICAL": "red",
        "HIGH": "volcano",
        "MEDIUM": "orange",
        "LOW": "green",
    }.get((level or "").upper(), "default")


@router.get("/kpis")
def executive_kpis(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    today = date.today()
    total_systems = _count(db, select(func.count(InformationSystem.id)))
    total_profiles = _count(db, select(func.count(LevelProfile.id)))
    level3_plus = _count(db, select(func.count(InformationSystem.id)).where(InformationSystem.proposed_level >= 3))
    approved_profiles = _count(db, select(func.count(LevelProfile.id)).where(LevelProfile.status.in_(["INTERNALLY_APPROVED", "APPROVAL_DECISION_ISSUED", "COMPLETED"])))
    pending_assessment = _count(db, select(func.count(AssessmentCase.id)).where(AssessmentCase.status.in_(["DRAFT", "SUBMITTED", "IN_REVIEW"])))
    open_feedbacks = _count(db, select(func.count(AssessmentFeedback.id)).where(AssessmentFeedback.status != "CLOSED"))
    open_risks = _count(db, select(func.count(RiskRegisterItem.id)).where(RiskRegisterItem.status != "CLOSED"))
    high_risks = _count(db, select(func.count(RiskRegisterItem.id)).where(RiskRegisterItem.status != "CLOSED", RiskRegisterItem.risk_level.in_(["HIGH", "CRITICAL"])))
    overdue_reviews = _count(db, select(func.count(PeriodicReview.id)).where(PeriodicReview.status != "COMPLETED", PeriodicReview.due_date < today))
    due_reviews = _count(db, select(func.count(PeriodicReview.id)).where(PeriodicReview.status != "COMPLETED", PeriodicReview.due_date <= today + timedelta(days=30)))
    mandatory_gap = _count(
        db,
        select(func.count(ProfileRequirementAnswer.id))
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(SecurityRequirement.is_mandatory.is_(True), ProfileRequirementAnswer.status == "NON_COMPLIANT"),
    )
    evidence_missing = _count(
        db,
        select(func.count(LevelProfile.id))
        .outerjoin(EvidenceDocument, EvidenceDocument.profile_id == LevelProfile.id)
        .group_by(LevelProfile.id)
        .having(func.count(EvidenceDocument.id) == 0)
        .subquery()
        .select(),
    ) if False else len(db.scalars(select(LevelProfile.id).outerjoin(EvidenceDocument, EvidenceDocument.profile_id == LevelProfile.id).group_by(LevelProfile.id).having(func.count(EvidenceDocument.id) == 0)).all())
    avg_compliance = _avg(db, select(func.avg(ComplianceScore.overall_score)))
    avg_risk_score = _avg(db, select(func.avg(RiskAssessment.risk_score)))

    severity_score = high_risks * 3 + overdue_reviews * 3 + mandatory_gap * 2 + open_feedbacks + evidence_missing
    if severity_score >= 20:
        executive_status = "CRITICAL"
    elif severity_score >= 10:
        executive_status = "ATTENTION_REQUIRED"
    elif severity_score >= 4:
        executive_status = "WATCH"
    else:
        executive_status = "NORMAL"

    return {
        "executive_status": executive_status,
        "severity_score": severity_score,
        "total_systems": total_systems,
        "level3_plus_systems": level3_plus,
        "total_profiles": total_profiles,
        "approved_profiles": approved_profiles,
        "approval_rate": round((approved_profiles / total_profiles * 100), 2) if total_profiles else 0,
        "average_compliance": avg_compliance,
        "average_risk_score": avg_risk_score,
        "mandatory_gap": mandatory_gap,
        "profiles_missing_evidence": evidence_missing,
        "overdue_reviews": overdue_reviews,
        "due_reviews_30_days": due_reviews,
        "open_risks": open_risks,
        "high_risks": high_risks,
        "pending_assessment_cases": pending_assessment,
        "open_assessment_feedbacks": open_feedbacks,
    }


@router.get("/portfolio")
def executive_portfolio(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    systems_by_level = _dict(db.execute(select(InformationSystem.proposed_level, func.count(InformationSystem.id)).group_by(InformationSystem.proposed_level)).all())
    profiles_by_status = _dict(db.execute(select(LevelProfile.status, func.count(LevelProfile.id)).group_by(LevelProfile.status)).all())
    risks_by_level = _dict(db.execute(select(RiskRegisterItem.risk_level, func.count(RiskRegisterItem.id)).where(RiskRegisterItem.status != "CLOSED").group_by(RiskRegisterItem.risk_level)).all())
    assessment_by_status = _dict(db.execute(select(AssessmentCase.status, func.count(AssessmentCase.id)).group_by(AssessmentCase.status)).all())
    reviews_by_status = _dict(db.execute(select(PeriodicReview.status, func.count(PeriodicReview.id)).group_by(PeriodicReview.status)).all())
    return {
        "systems_by_level": systems_by_level,
        "profiles_by_status": profiles_by_status,
        "risks_by_level": risks_by_level,
        "assessment_by_status": assessment_by_status,
        "reviews_by_status": reviews_by_status,
    }


@router.get("/priority-actions")
def executive_priority_actions(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    today = date.today()
    risk_rows = db.execute(
        select(RiskRegisterItem.id, RiskRegisterItem.risk_code, RiskRegisterItem.title, RiskRegisterItem.risk_level, RiskRegisterItem.risk_score, RiskRegisterItem.owner, RiskRegisterItem.due_date)
        .where(RiskRegisterItem.status != "CLOSED")
        .order_by(RiskRegisterItem.risk_score.desc(), RiskRegisterItem.due_date.asc().nullslast())
        .limit(10)
    ).all()
    gap_rows = db.execute(
        select(ProfileRequirementAnswer.id, LevelProfile.profile_code, SecurityRequirement.code, SecurityRequirement.title, ProfileRequirementAnswer.owner, ProfileRequirementAnswer.due_date)
        .join(LevelProfile, ProfileRequirementAnswer.profile_id == LevelProfile.id)
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(SecurityRequirement.is_mandatory.is_(True), ProfileRequirementAnswer.status == "NON_COMPLIANT")
        .order_by(ProfileRequirementAnswer.due_date.asc().nullslast(), LevelProfile.proposed_level.desc())
        .limit(10)
    ).all()
    review_rows = db.execute(
        select(PeriodicReview.id, PeriodicReview.review_code, PeriodicReview.profile_id, PeriodicReview.status, PeriodicReview.due_date)
        .where(PeriodicReview.status != "COMPLETED", PeriodicReview.due_date <= today + timedelta(days=30))
        .order_by(PeriodicReview.due_date.asc())
        .limit(10)
    ).all()
    feedback_rows = db.execute(
        select(AssessmentFeedback.id, AssessmentFeedback.title, AssessmentFeedback.severity, AssessmentFeedback.status, AssessmentFeedback.profile_id)
        .where(AssessmentFeedback.status != "CLOSED")
        .order_by(AssessmentFeedback.severity.desc(), AssessmentFeedback.id.desc())
        .limit(10)
    ).all()
    return {
        "top_risks": [
            {"id": r.id, "code": r.risk_code, "title": r.title, "risk_level": r.risk_level, "risk_color": _risk_color(r.risk_level), "risk_score": r.risk_score, "owner": r.owner, "due_date": r.due_date.isoformat() if r.due_date else None}
            for r in risk_rows
        ],
        "mandatory_gaps": [
            {"id": r.id, "profile_code": r.profile_code, "requirement_code": r.code, "title": r.title, "owner": r.owner, "due_date": r.due_date.isoformat() if r.due_date else None}
            for r in gap_rows
        ],
        "due_reviews": [
            {"id": r.id, "review_code": r.review_code, "profile_id": r.profile_id, "status": r.status, "due_date": r.due_date.isoformat() if r.due_date else None}
            for r in review_rows
        ],
        "assessment_feedbacks": [
            {"id": r.id, "title": r.title, "severity": r.severity, "status": r.status, "profile_id": r.profile_id}
            for r in feedback_rows
        ],
    }


@router.get("/board-pack")
def executive_board_pack(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    kpis = executive_kpis(db, current_user)
    portfolio = executive_portfolio(db, current_user)
    actions = executive_priority_actions(db, current_user)
    recommendations = []
    if kpis["high_risks"]:
        recommendations.append("Ưu tiên xử lý các rủi ro HIGH/CRITICAL trước khi gửi thẩm định hoặc phê duyệt chính thức.")
    if kpis["mandatory_gap"]:
        recommendations.append("Yêu cầu các đơn vị hoàn thiện tiêu chí bắt buộc chưa đáp ứng và bổ sung minh chứng.")
    if kpis["overdue_reviews"]:
        recommendations.append("Rà soát ngay các hồ sơ quá hạn để tránh không tuân thủ chu kỳ đánh giá định kỳ.")
    if not recommendations:
        recommendations.append("Danh mục hồ sơ đang trong trạng thái kiểm soát; tiếp tục theo dõi định kỳ và cập nhật minh chứng.")
    return {
        "generated_at": date.today().isoformat(),
        "title": "Executive Board Pack - Hồ sơ đề xuất cấp độ ATHTTT",
        "kpis": kpis,
        "portfolio": portfolio,
        "priority_actions": actions,
        "recommendations": recommendations,
    }
