from __future__ import annotations

from datetime import date, datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.level_profile import LevelProfile
from app.models.periodic_review import PeriodicReview
from app.models.user import User
from app.services.audit_service import write_audit_log
from app.services.notification_service import create_notification


def _add_months(base: date, months: int) -> date:
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def build_review_code(profile: LevelProfile, due_date: date) -> str:
    return f"RV-{profile.profile_code}-{due_date.strftime('%Y%m%d')}"


def create_review(
    db: Session,
    profile: LevelProfile,
    *,
    due_date: date,
    review_type: str = "ANNUAL",
    assigned_to: int | None = None,
    created_by: int | None = None,
    note: str | None = None,
) -> PeriodicReview:
    code = build_review_code(profile, due_date)
    exists = db.scalar(select(PeriodicReview).where(PeriodicReview.review_code == code))
    if exists:
        return exists
    review = PeriodicReview(
        profile_id=profile.id,
        review_code=code,
        review_type=review_type.upper(),
        status="PLANNED",
        due_date=due_date,
        assigned_to=assigned_to,
        created_by=created_by,
        note=note,
    )
    db.add(review)
    db.flush()
    write_audit_log(db, action="CREATE_PERIODIC_REVIEW", entity_type="periodic_review", entity_id=review.id, actor_id=created_by, detail=f"Create review {code}")
    return review


def generate_next_review(db: Session, profile: LevelProfile, *, months: int = 12, assigned_to: int | None = None, created_by: int | None = None, note: str | None = None) -> PeriodicReview:
    last_due = db.scalar(select(func.max(PeriodicReview.due_date)).where(PeriodicReview.profile_id == profile.id))
    base_date = last_due or date.today()
    return create_review(db, profile, due_date=_add_months(base_date, months), review_type="ANNUAL", assigned_to=assigned_to, created_by=created_by, note=note)


def mark_in_progress_if_needed(review: PeriodicReview) -> None:
    if review.status == "PLANNED":
        review.status = "IN_PROGRESS"


def complete_review(db: Session, review: PeriodicReview, *, findings: str, action_plan: str | None, completed_by: int | None) -> PeriodicReview:
    review.status = "COMPLETED"
    review.findings = findings
    review.action_plan = action_plan
    review.completed_by = completed_by
    review.completed_at = datetime.utcnow()
    write_audit_log(db, action="COMPLETE_PERIODIC_REVIEW", entity_type="periodic_review", entity_id=review.id, actor_id=completed_by, detail=f"Complete review {review.review_code}")
    return review


def get_due_soon_reviews(db: Session, days: int = 30) -> list[PeriodicReview]:
    today = date.today()
    until = today + timedelta(days=days)
    return db.scalars(
        select(PeriodicReview)
        .where(PeriodicReview.status != "COMPLETED", PeriodicReview.due_date <= until)
        .order_by(PeriodicReview.due_date.asc())
    ).all()


def send_review_reminders(db: Session, *, days: int = 30, recipient: str = "attt@example.com", created_by: int | None = None) -> dict:
    reviews = get_due_soon_reviews(db, days=days)
    sent = 0
    for review in reviews:
        create_notification(
            db,
            event_type="PERIODIC_REVIEW_REMINDER",
            channel="IN_APP",
            recipient=recipient,
            subject=f"Nhắc rà soát hồ sơ {review.review_code}",
            message=f"Lịch rà soát {review.review_code} đến hạn ngày {review.due_date}. Trạng thái hiện tại: {review.status}.",
            related_profile_id=review.profile_id,
            created_by=created_by,
        )
        sent += 1
    return {"due_soon_count": len(reviews), "notification_created": sent}
