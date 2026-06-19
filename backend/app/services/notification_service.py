from datetime import datetime
from sqlalchemy.orm import Session

from app.models.notification_log import NotificationLog


SUPPORTED_CHANNELS = {"IN_APP", "EMAIL", "TELEGRAM"}


def create_notification(
    db: Session,
    *,
    event_type: str,
    channel: str,
    recipient: str,
    subject: str,
    message: str,
    related_profile_id: int | None = None,
    created_by: int | None = None,
) -> NotificationLog:
    channel = channel.upper().strip()
    if channel not in SUPPORTED_CHANNELS:
        channel = "IN_APP"

    # MVP mode: do not really send email/telegram yet. Record a SENT log so that
    # workflow/dashboard can be tested end-to-end. Real adapters will be added later.
    log = NotificationLog(
        event_type=event_type.upper().strip(),
        channel=channel,
        recipient=recipient,
        subject=subject,
        message=message,
        status="SENT",
        related_profile_id=related_profile_id,
        sent_at=datetime.utcnow(),
        created_by=created_by,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
