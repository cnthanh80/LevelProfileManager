from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.level_profile import LevelProfile
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.security_requirement import SecurityRequirement

VALID_STATUSES = {"COMPLIANT", "NON_COMPLIANT", "NOT_APPLICABLE"}


def validate_answer_status(status: str | None) -> None:
    if status is not None and status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {', '.join(sorted(VALID_STATUSES))}")


def generate_checklist_for_profile(db: Session, profile_id: int) -> dict:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Level profile not found")

    requirements = db.scalars(
        select(SecurityRequirement)
        .where(SecurityRequirement.required_level <= profile.proposed_level)
        .order_by(SecurityRequirement.required_level, SecurityRequirement.group_name, SecurityRequirement.sort_order, SecurityRequirement.code)
    ).all()

    created = 0
    existing = 0
    for requirement in requirements:
        existed = db.scalar(
            select(ProfileRequirementAnswer).where(
                ProfileRequirementAnswer.profile_id == profile_id,
                ProfileRequirementAnswer.requirement_id == requirement.id,
            )
        )
        if existed:
            existing += 1
            continue
        db.add(
            ProfileRequirementAnswer(
                profile_id=profile_id,
                requirement_id=requirement.id,
                status="NON_COMPLIANT" if requirement.is_mandatory else "NOT_APPLICABLE",
            )
        )
        created += 1
    db.commit()
    return {
        "profile_id": profile.id,
        "proposed_level": profile.proposed_level,
        "created": created,
        "existing": existing,
        "total": len(requirements),
    }


def build_compliance_summary(db: Session, profile_id: int) -> dict:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Level profile not found")

    rows = db.execute(
        select(ProfileRequirementAnswer, SecurityRequirement)
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(ProfileRequirementAnswer.profile_id == profile_id)
        .order_by(SecurityRequirement.group_name, SecurityRequirement.category, SecurityRequirement.sort_order, SecurityRequirement.code)
    ).all()

    total = len(rows)
    compliant = sum(1 for answer, _ in rows if answer.status == "COMPLIANT")
    non_compliant = sum(1 for answer, _ in rows if answer.status == "NON_COMPLIANT")
    not_applicable = sum(1 for answer, _ in rows if answer.status == "NOT_APPLICABLE")
    mandatory_total = sum(1 for _, req in rows if req.is_mandatory)
    mandatory_non_compliant = sum(1 for answer, req in rows if req.is_mandatory and answer.status == "NON_COMPLIANT")

    by_group: dict[str, dict] = {}
    warnings: list[str] = []
    for answer, req in rows:
        group = req.group_name
        if group not in by_group:
            by_group[group] = {
                "total": 0,
                "compliant": 0,
                "non_compliant": 0,
                "not_applicable": 0,
                "mandatory_total": 0,
                "mandatory_non_compliant": 0,
                "compliance_percent": 0.0,
            }
        bucket = by_group[group]
        bucket["total"] += 1
        bucket["compliant"] += 1 if answer.status == "COMPLIANT" else 0
        bucket["non_compliant"] += 1 if answer.status == "NON_COMPLIANT" else 0
        bucket["not_applicable"] += 1 if answer.status == "NOT_APPLICABLE" else 0
        bucket["mandatory_total"] += 1 if req.is_mandatory else 0
        if req.is_mandatory and answer.status == "NON_COMPLIANT":
            bucket["mandatory_non_compliant"] += 1
            warnings.append(f"{req.code} - {req.title}")

    for bucket in by_group.values():
        denominator = bucket["total"] - bucket["not_applicable"]
        bucket["compliance_percent"] = round(bucket["compliant"] * 100 / denominator, 2) if denominator else 100.0

    denominator = total - not_applicable
    overall_percent = round(compliant * 100 / denominator, 2) if denominator else 100.0
    return {
        "profile_id": profile.id,
        "proposed_level": profile.proposed_level,
        "total": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "not_applicable": not_applicable,
        "mandatory_total": mandatory_total,
        "mandatory_non_compliant": mandatory_non_compliant,
        "overall_percent": overall_percent,
        "by_group": by_group,
        "warnings": warnings[:50],
    }
