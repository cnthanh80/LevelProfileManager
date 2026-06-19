from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.level_profile import LevelProfile
from app.models.notification_log import NotificationLog
from app.models.periodic_review import PeriodicReview
from app.models.user import User
from app.schemas.common import Page
from app.schemas.notification import (
    BulkReminderRequest,
    NotificationCreate,
    NotificationLogRead,
    NotificationRuntimeStatus,
    NotificationSummary,
    ProfileReminderCreate,
)
from app.services.notification_service import create_notification, get_notification_runtime_status

router = APIRouter()


@router.get("/notifications", response_model=Page[NotificationLogRead])
def list_notifications(
    db: Session = Depends(get_db),
    channel: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    event_type: str | None = Query(default=None),
    related_profile_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
):
    stmt = select(NotificationLog)
    count_stmt = select(func.count(NotificationLog.id))
    filters = []
    if channel:
        filters.append(NotificationLog.channel == channel.upper())
    if status_filter:
        filters.append(NotificationLog.status == status_filter.upper())
    if event_type:
        filters.append(NotificationLog.event_type == event_type.upper())
    if related_profile_id is not None:
        filters.append(NotificationLog.related_profile_id == related_profile_id)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(NotificationLog.created_at.desc(), NotificationLog.id.desc()).limit(limit).offset(offset)).all()
    return Page[NotificationLogRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/notifications/summary", response_model=NotificationSummary)
def notification_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(select(func.count(NotificationLog.id))) or 0
    pending = db.scalar(select(func.count(NotificationLog.id)).where(NotificationLog.status == "PENDING")) or 0
    sent = db.scalar(select(func.count(NotificationLog.id)).where(NotificationLog.status == "SENT")) or 0
    failed = db.scalar(select(func.count(NotificationLog.id)).where(NotificationLog.status == "FAILED")) or 0

    by_channel_rows = db.execute(select(NotificationLog.channel, func.count(NotificationLog.id)).group_by(NotificationLog.channel)).all()
    by_event_rows = db.execute(select(NotificationLog.event_type, func.count(NotificationLog.id)).group_by(NotificationLog.event_type)).all()
    return NotificationSummary(
        total=total,
        pending=pending,
        sent=sent,
        failed=failed,
        by_channel={row[0]: row[1] for row in by_channel_rows},
        by_event_type={row[0]: row[1] for row in by_event_rows},
    )


@router.get("/notifications/runtime-status", response_model=NotificationRuntimeStatus)
def notification_runtime_status(
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return get_notification_runtime_status()


@router.post("/notifications/send-test", response_model=NotificationLogRead, status_code=status.HTTP_201_CREATED)
def send_test_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return create_notification(
        db,
        event_type=payload.event_type,
        channel=payload.channel,
        recipient=payload.recipient,
        subject=payload.subject,
        message=payload.message,
        related_profile_id=payload.related_profile_id,
        created_by=current_user.id,
    )


@router.post("/notifications/send-email-test", response_model=NotificationLogRead, status_code=status.HTTP_201_CREATED)
def send_email_test(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    payload.channel = "EMAIL"
    return create_notification(
        db,
        event_type=payload.event_type or "EMAIL_TEST",
        channel="EMAIL",
        recipient=payload.recipient,
        subject=payload.subject,
        message=payload.message,
        related_profile_id=payload.related_profile_id,
        created_by=current_user.id,
    )


@router.post("/notifications/send-telegram-test", response_model=NotificationLogRead, status_code=status.HTTP_201_CREATED)
def send_telegram_test(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return create_notification(
        db,
        event_type=payload.event_type or "TELEGRAM_TEST",
        channel="TELEGRAM",
        recipient=payload.recipient,
        subject=payload.subject,
        message=payload.message,
        related_profile_id=payload.related_profile_id,
        created_by=current_user.id,
    )


@router.post("/profiles/{profile_id}/notifications/review-reminder", response_model=NotificationLogRead, status_code=status.HTTP_201_CREATED)
def send_profile_review_reminder(
    profile_id: int,
    payload: ProfileReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER", "APPROVER")),
):
    profile = db.get(LevelProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    subject = payload.subject or f"Nhắc xử lý hồ sơ {profile.profile_code}"
    message = payload.message or f"Hồ sơ {profile.profile_code} đang ở trạng thái {profile.status}. Vui lòng kiểm tra và xử lý theo phân quyền."
    return create_notification(
        db,
        event_type="PROFILE_REVIEW_REMINDER",
        channel=payload.channel,
        recipient=payload.recipient,
        subject=subject,
        message=message,
        related_profile_id=profile_id,
        created_by=current_user.id,
    )


@router.post("/notifications/send-due-review-reminders")
def send_due_review_reminders(
    payload: BulkReminderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    rows = db.scalars(
        select(PeriodicReview)
        .where(PeriodicReview.status != "COMPLETED")
        .order_by(PeriodicReview.due_date.asc())
    ).all()
    sent = 0
    for review in rows:
        log = create_notification(
            db,
            event_type="PERIODIC_REVIEW_REMINDER",
            channel=payload.channel,
            recipient=payload.recipient,
            subject=f"Nhắc rà soát hồ sơ {review.review_code}",
            message=f"Lịch rà soát {review.review_code} đến hạn ngày {review.due_date}. Trạng thái hiện tại: {review.status}.",
            related_profile_id=review.profile_id,
            created_by=current_user.id,
        )
        if log.status == "SENT":
            sent += 1
    return {"candidate_count": len(rows), "sent_count": sent, "channel": payload.channel.upper()}
