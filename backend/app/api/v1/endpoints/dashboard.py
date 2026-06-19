from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.evidence_document import EvidenceDocument
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.security_requirement import SecurityRequirement
from app.models.user import User

router = APIRouter(prefix="/dashboard")


def _rows_to_dict(rows) -> dict:
    return {str(key): int(value) for key, value in rows if key is not None}


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    total_systems = db.scalar(select(func.count(InformationSystem.id))) or 0
    total_profiles = db.scalar(select(func.count(LevelProfile.id))) or 0
    total_documents = db.scalar(select(func.count(EvidenceDocument.id))) or 0
    total_requirements = db.scalar(select(func.count(SecurityRequirement.id))) or 0

    systems_by_level = _rows_to_dict(
        db.execute(
            select(InformationSystem.proposed_level, func.count(InformationSystem.id))
            .group_by(InformationSystem.proposed_level)
            .order_by(InformationSystem.proposed_level)
        ).all()
    )
    profiles_by_status = _rows_to_dict(
        db.execute(
            select(LevelProfile.status, func.count(LevelProfile.id))
            .group_by(LevelProfile.status)
            .order_by(LevelProfile.status)
        ).all()
    )
    profiles_by_level = _rows_to_dict(
        db.execute(
            select(LevelProfile.proposed_level, func.count(LevelProfile.id))
            .group_by(LevelProfile.proposed_level)
            .order_by(LevelProfile.proposed_level)
        ).all()
    )

    high_level_systems = db.execute(
        select(InformationSystem.id, InformationSystem.code, InformationSystem.name, InformationSystem.proposed_level)
        .where(InformationSystem.proposed_level >= 3)
        .order_by(InformationSystem.proposed_level.desc(), InformationSystem.code)
        .limit(20)
    ).all()

    profiles_without_documents = db.execute(
        select(LevelProfile.id, LevelProfile.profile_code, LevelProfile.proposed_level, LevelProfile.status)
        .outerjoin(EvidenceDocument, EvidenceDocument.profile_id == LevelProfile.id)
        .group_by(LevelProfile.id, LevelProfile.profile_code, LevelProfile.proposed_level, LevelProfile.status)
        .having(func.count(EvidenceDocument.id) == 0)
        .order_by(LevelProfile.id)
        .limit(20)
    ).all()

    mandatory_not_met = db.scalar(
        select(func.count(ProfileRequirementAnswer.id))
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(SecurityRequirement.is_mandatory.is_(True), ProfileRequirementAnswer.status == "NON_COMPLIANT")
    ) or 0

    return {
        "total_systems": total_systems,
        "total_profiles": total_profiles,
        "total_documents": total_documents,
        "total_requirements": total_requirements,
        "systems_by_level": systems_by_level,
        "profiles_by_level": profiles_by_level,
        "profiles_by_status": profiles_by_status,
        "high_level_systems": [
            {"id": r.id, "code": r.code, "name": r.name, "proposed_level": r.proposed_level}
            for r in high_level_systems
        ],
        "profiles_without_documents": [
            {"id": r.id, "profile_code": r.profile_code, "proposed_level": r.proposed_level, "status": r.status}
            for r in profiles_without_documents
        ],
        "mandatory_not_met": mandatory_not_met,
    }


@router.get("/workflow-summary")
def get_workflow_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = db.execute(
        select(LevelProfile.status, func.count(LevelProfile.id))
        .group_by(LevelProfile.status)
        .order_by(LevelProfile.status)
    ).all()
    return {"profiles_by_status": _rows_to_dict(rows)}


@router.get("/compliance-overview")
def get_compliance_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = db.execute(
        select(LevelProfile.id, LevelProfile.profile_code, LevelProfile.proposed_level)
        .order_by(LevelProfile.id)
    ).all()

    items = []
    for profile in rows:
        total = db.scalar(
            select(func.count(ProfileRequirementAnswer.id))
            .where(ProfileRequirementAnswer.profile_id == profile.id)
        ) or 0
        compliant = db.scalar(
            select(func.count(ProfileRequirementAnswer.id))
            .where(ProfileRequirementAnswer.profile_id == profile.id, ProfileRequirementAnswer.status == "COMPLIANT")
        ) or 0
        not_applicable = db.scalar(
            select(func.count(ProfileRequirementAnswer.id))
            .where(ProfileRequirementAnswer.profile_id == profile.id, ProfileRequirementAnswer.status == "NOT_APPLICABLE")
        ) or 0
        mandatory_not_met = db.scalar(
            select(func.count(ProfileRequirementAnswer.id))
            .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
            .where(
                ProfileRequirementAnswer.profile_id == profile.id,
                SecurityRequirement.is_mandatory.is_(True),
                ProfileRequirementAnswer.status == "NON_COMPLIANT",
            )
        ) or 0
        denominator = total - not_applicable
        compliance_percent = round(compliant * 100 / denominator, 2) if denominator else 0.0
        items.append(
            {
                "profile_id": profile.id,
                "profile_code": profile.profile_code,
                "proposed_level": profile.proposed_level,
                "total_answers": total,
                "compliant": compliant,
                "not_applicable": not_applicable,
                "mandatory_not_met": mandatory_not_met,
                "compliance_percent": compliance_percent,
            }
        )

    avg = round(sum(i["compliance_percent"] for i in items) / len(items), 2) if items else 0.0
    return {"average_compliance_percent": avg, "items": items}


@router.get("/evidence-gaps")
def get_evidence_gaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profiles_without_documents = db.execute(
        select(LevelProfile.id, LevelProfile.profile_code, LevelProfile.proposed_level, LevelProfile.status)
        .outerjoin(EvidenceDocument, EvidenceDocument.profile_id == LevelProfile.id)
        .group_by(LevelProfile.id, LevelProfile.profile_code, LevelProfile.proposed_level, LevelProfile.status)
        .having(func.count(EvidenceDocument.id) == 0)
        .order_by(LevelProfile.id)
    ).all()

    mandatory_answers_without_evidence = db.execute(
        select(
            ProfileRequirementAnswer.id,
            LevelProfile.profile_code,
            SecurityRequirement.code,
            SecurityRequirement.title,
            ProfileRequirementAnswer.status,
        )
        .join(LevelProfile, ProfileRequirementAnswer.profile_id == LevelProfile.id)
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(
            SecurityRequirement.is_mandatory.is_(True),
            ProfileRequirementAnswer.status == "COMPLIANT",
            ProfileRequirementAnswer.evidence_count == 0,
        )
        .order_by(LevelProfile.profile_code, SecurityRequirement.code)
        .limit(100)
    ).all()

    return {
        "profiles_without_documents": [
            {"id": r.id, "profile_code": r.profile_code, "proposed_level": r.proposed_level, "status": r.status}
            for r in profiles_without_documents
        ],
        "mandatory_compliant_answers_without_evidence": [
            {
                "answer_id": r.id,
                "profile_code": r.profile_code,
                "requirement_code": r.code,
                "requirement_title": r.title,
                "status": r.status,
            }
            for r in mandatory_answers_without_evidence
        ],
    }
