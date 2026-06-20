from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.assessment_portal import AssessmentCase, AssessmentFeedback
from app.models.level_profile import LevelProfile
from app.models.user import User
from app.schemas.assessment_portal import (
    AssessmentCaseCreate,
    AssessmentCaseRead,
    AssessmentCaseUpdate,
    AssessmentFeedbackCreate,
    AssessmentFeedbackRead,
    AssessmentFeedbackResponse,
    AssessmentFeedbackUpdate,
    AssessmentPortalSummary,
)
from app.schemas.common import Page
from app.services.assessment_portal_service import complete_case, get_assessment_summary, normalize_case, normalize_feedback, submit_case

router = APIRouter()


@router.get("/assessment-portal/summary", response_model=AssessmentPortalSummary)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_assessment_summary(db)


@router.get("/assessment-cases", response_model=Page[AssessmentCaseRead])
def list_cases(
    profile_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(AssessmentCase)
    count_stmt = select(func.count(AssessmentCase.id))
    filters = []
    if profile_id:
        filters.append(AssessmentCase.profile_id == profile_id)
    if status_filter:
        filters.append(AssessmentCase.status == status_filter.upper())
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(AssessmentCase.id.desc()).limit(limit).offset(offset)).all()
    return Page[AssessmentCaseRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/assessment-cases", response_model=AssessmentCaseRead, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: AssessmentCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    profile = db.get(LevelProfile, payload.profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    existing = db.scalar(select(AssessmentCase).where(AssessmentCase.case_code == payload.case_code))
    if existing:
        raise HTTPException(status_code=409, detail="Assessment case code already exists")
    data = payload.model_dump()
    case = AssessmentCase(**data, created_by=current_user.id)
    normalize_case(case)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("/assessment-cases/{case_id}", response_model=AssessmentCaseRead)
def get_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.get(AssessmentCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Assessment case not found")
    return case


@router.put("/assessment-cases/{case_id}", response_model=AssessmentCaseRead)
def update_case(
    case_id: int,
    payload: AssessmentCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    case = db.get(AssessmentCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Assessment case not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(case, key, value)
    normalize_case(case)
    db.commit()
    db.refresh(case)
    return case


@router.post("/assessment-cases/{case_id}/submit", response_model=AssessmentCaseRead)
def submit_assessment_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    case = db.get(AssessmentCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Assessment case not found")
    return submit_case(db, case)


@router.post("/assessment-cases/{case_id}/complete", response_model=AssessmentCaseRead)
def complete_assessment_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "APPROVER")),
):
    case = db.get(AssessmentCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Assessment case not found")
    return complete_case(db, case)


@router.get("/assessment-feedbacks", response_model=Page[AssessmentFeedbackRead])
def list_feedbacks(
    case_id: int | None = None,
    profile_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(AssessmentFeedback)
    count_stmt = select(func.count(AssessmentFeedback.id))
    filters = []
    if case_id:
        filters.append(AssessmentFeedback.case_id == case_id)
    if profile_id:
        filters.append(AssessmentFeedback.profile_id == profile_id)
    if status_filter:
        filters.append(AssessmentFeedback.status == status_filter.upper())
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(AssessmentFeedback.id.desc()).limit(limit).offset(offset)).all()
    return Page[AssessmentFeedbackRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/assessment-feedbacks", response_model=AssessmentFeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: AssessmentFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    case = db.get(AssessmentCase, payload.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Assessment case not found")
    feedback = AssessmentFeedback(**payload.model_dump(), created_by=current_user.id)
    normalize_feedback(feedback)
    db.add(feedback)
    case.status = "COMMENTED"
    db.commit()
    db.refresh(feedback)
    return feedback


@router.put("/assessment-feedbacks/{feedback_id}", response_model=AssessmentFeedbackRead)
def update_feedback(
    feedback_id: int,
    payload: AssessmentFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    feedback = db.get(AssessmentFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Assessment feedback not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(feedback, key, value)
    normalize_feedback(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.post("/assessment-feedbacks/{feedback_id}/respond", response_model=AssessmentFeedbackRead)
def respond_feedback(
    feedback_id: int,
    payload: AssessmentFeedbackResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    feedback = db.get(AssessmentFeedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Assessment feedback not found")
    feedback.response = payload.response
    feedback.status = payload.status.upper()
    feedback.responded_by = current_user.id
    from datetime import datetime
    feedback.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(feedback)
    return feedback
