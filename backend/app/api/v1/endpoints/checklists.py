from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.level_profile import LevelProfile
from app.models.profile_requirement_answer import ProfileRequirementAnswer
from app.models.security_requirement import SecurityRequirement
from app.schemas.checklist import (
    ChecklistAnswerRead,
    ChecklistAnswerUpdate,
    ChecklistGenerateResponse,
    ChecklistItemRead,
    ComplianceSummary,
)
from app.services.checklist_service import build_compliance_summary, generate_checklist_for_profile, validate_answer_status

router = APIRouter()


@router.post("/profiles/{profile_id}/generate-checklist", response_model=ChecklistGenerateResponse)
def generate_profile_checklist(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return generate_checklist_for_profile(db, profile_id)


@router.get("/profiles/{profile_id}/checklist", response_model=list[ChecklistItemRead])
def get_profile_checklist(
    profile_id: int,
    db: Session = Depends(get_db),
    status_value: str | None = Query(default=None, alias="status"),
    group_name: str | None = Query(default=None),
):
    if db.get(LevelProfile, profile_id) is None:
        raise HTTPException(status_code=404, detail="Level profile not found")

    stmt = (
        select(ProfileRequirementAnswer, SecurityRequirement)
        .join(SecurityRequirement, ProfileRequirementAnswer.requirement_id == SecurityRequirement.id)
        .where(ProfileRequirementAnswer.profile_id == profile_id)
        .order_by(SecurityRequirement.group_name, SecurityRequirement.category, SecurityRequirement.sort_order, SecurityRequirement.code)
    )
    if status_value:
        validate_answer_status(status_value)
        stmt = stmt.where(ProfileRequirementAnswer.status == status_value)
    if group_name:
        stmt = stmt.where(SecurityRequirement.group_name == group_name)

    items = []
    for answer, requirement in db.execute(stmt).all():
        data = ChecklistAnswerRead.model_validate(answer).model_dump()
        data["requirement"] = requirement
        items.append(data)
    return items


@router.put("/checklist-answers/{answer_id}", response_model=ChecklistAnswerRead)
def update_checklist_answer(
    answer_id: int,
    payload: ChecklistAnswerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER", "OPERATOR", "REVIEWER")),
):
    item = db.get(ProfileRequirementAnswer, answer_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist answer not found")
    data = payload.model_dump(exclude_unset=True)
    validate_answer_status(data.get("status"))
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.get("/profiles/{profile_id}/compliance-summary", response_model=ComplianceSummary)
def get_profile_compliance_summary(profile_id: int, db: Session = Depends(get_db)):
    return build_compliance_summary(db, profile_id)
