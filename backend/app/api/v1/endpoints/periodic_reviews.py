from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.level_profile import LevelProfile
from app.models.periodic_review import PeriodicReview
from app.models.user import User
from app.schemas.common import Page
from app.schemas.periodic_review import (
    GenerateNextReviewRequest,
    PeriodicReviewComplete,
    PeriodicReviewCreate,
    PeriodicReviewRead,
    PeriodicReviewUpdate,
    ReviewSummary,
)
from app.services.periodic_review_service import complete_review, create_review, generate_next_review, get_due_soon_reviews, send_review_reminders

router = APIRouter()


def _profile_or_404(db: Session, profile_id: int) -> LevelProfile:
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def _review_or_404(db: Session, review_id: int) -> PeriodicReview:
    review = db.get(PeriodicReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Periodic review not found")
    return review


@router.post("/profiles/{profile_id}/periodic-reviews", response_model=PeriodicReviewRead, status_code=status.HTTP_201_CREATED)
def create_profile_periodic_review(
    profile_id: int,
    payload: PeriodicReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    profile = _profile_or_404(db, profile_id)
    review = create_review(
        db,
        profile,
        due_date=payload.due_date,
        review_type=payload.review_type,
        assigned_to=payload.assigned_to,
        created_by=current_user.id,
        note=payload.note,
    )
    db.commit()
    db.refresh(review)
    return review


@router.post("/profiles/{profile_id}/periodic-reviews/generate-next", response_model=PeriodicReviewRead, status_code=status.HTTP_201_CREATED)
def generate_next_profile_review(
    profile_id: int,
    payload: GenerateNextReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    profile = _profile_or_404(db, profile_id)
    review = generate_next_review(db, profile, months=payload.months, assigned_to=payload.assigned_to, created_by=current_user.id, note=payload.note)
    db.commit()
    db.refresh(review)
    return review


@router.get("/profiles/{profile_id}/periodic-reviews", response_model=Page[PeriodicReviewRead])
def list_profile_periodic_reviews(
    profile_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    _profile_or_404(db, profile_id)
    total = db.scalar(select(func.count(PeriodicReview.id)).where(PeriodicReview.profile_id == profile_id)) or 0
    items = db.scalars(
        select(PeriodicReview)
        .where(PeriodicReview.profile_id == profile_id)
        .order_by(PeriodicReview.due_date.desc(), PeriodicReview.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return Page[PeriodicReviewRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/periodic-reviews/due-soon", response_model=list[PeriodicReviewRead])
def due_soon_reviews(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_due_soon_reviews(db, days=days)


@router.put("/periodic-reviews/{review_id}", response_model=PeriodicReviewRead)
def update_periodic_review(
    review_id: int,
    payload: PeriodicReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    review = _review_or_404(db, review_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"]:
        data["status"] = data["status"].upper()
    for key, value in data.items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    return review


@router.post("/periodic-reviews/{review_id}/complete", response_model=PeriodicReviewRead)
def complete_periodic_review(
    review_id: int,
    payload: PeriodicReviewComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER", "APPROVER")),
):
    review = _review_or_404(db, review_id)
    review = complete_review(db, review, findings=payload.findings, action_plan=payload.action_plan, completed_by=current_user.id)
    db.commit()
    db.refresh(review)
    return review


@router.post("/periodic-reviews/send-reminders")
def create_periodic_review_reminders(
    days: int = Query(default=30, ge=1, le=365),
    recipient: str = Query(default="attt@example.com"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    result = send_review_reminders(db, days=days, recipient=recipient, created_by=current_user.id)
    db.commit()
    return result


@router.get("/dashboard/periodic-reviews", response_model=ReviewSummary)
def periodic_review_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    due_soon_date = today + timedelta(days=30)
    total = db.scalar(select(func.count(PeriodicReview.id))) or 0
    planned = db.scalar(select(func.count(PeriodicReview.id)).where(PeriodicReview.status == "PLANNED")) or 0
    in_progress = db.scalar(select(func.count(PeriodicReview.id)).where(PeriodicReview.status == "IN_PROGRESS")) or 0
    completed = db.scalar(select(func.count(PeriodicReview.id)).where(PeriodicReview.status == "COMPLETED")) or 0
    overdue = db.scalar(select(func.count(PeriodicReview.id)).where(PeriodicReview.status != "COMPLETED", PeriodicReview.due_date < today)) or 0
    due_soon = db.scalar(select(func.count(PeriodicReview.id)).where(PeriodicReview.status != "COMPLETED", PeriodicReview.due_date >= today, PeriodicReview.due_date <= due_soon_date)) or 0
    return ReviewSummary(total=total, planned=planned, in_progress=in_progress, completed=completed, overdue=overdue, due_soon=due_soon)
