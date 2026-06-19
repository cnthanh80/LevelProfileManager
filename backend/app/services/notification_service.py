from __future__ import annotations

from datetime import datetime
from email.message import EmailMessage
import json
import smtplib
import ssl
from urllib import request, parse, error

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification_log import NotificationLog


SUPPORTED_CHANNELS = {"IN_APP", "EMAIL", "TELEGRAM"}


class NotificationSendResult:
    def __init__(self, status: str, error_message: str | None = None):
        self.status = status
        self.error_message = error_message


def _normalize_channel(channel: str) -> str:
    value = (channel or "IN_APP").upper().strip()
    return value if value in SUPPORTED_CHANNELS else "IN_APP"


def _send_email(*, recipient: str, subject: str, message: str) -> NotificationSendResult:
    if settings.NOTIFICATION_DRY_RUN:
        return NotificationSendResult("SENT")
    if not settings.SMTP_ENABLED:
        return NotificationSendResult("FAILED", "SMTP is disabled. Set SMTP_ENABLED=true or use NOTIFICATION_DRY_RUN=true.")
    if not settings.SMTP_HOST:
        return NotificationSendResult("FAILED", "SMTP_HOST is not configured.")

    try:
        email = EmailMessage()
        email["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(message)

        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT_SECONDS) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls(context=context)
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
            smtp.send_message(email)
        return NotificationSendResult("SENT")
    except Exception as exc:  # noqa: BLE001 - we need to record operational error in DB
        return NotificationSendResult("FAILED", str(exc))


def _send_telegram(*, recipient: str, subject: str, message: str) -> NotificationSendResult:
    if settings.NOTIFICATION_DRY_RUN:
        return NotificationSendResult("SENT")
    if not settings.TELEGRAM_ENABLED:
        return NotificationSendResult("FAILED", "Telegram is disabled. Set TELEGRAM_ENABLED=true or use NOTIFICATION_DRY_RUN=true.")
    if not settings.TELEGRAM_BOT_TOKEN:
        return NotificationSendResult("FAILED", "TELEGRAM_BOT_TOKEN is not configured.")

    chat_id = recipient or settings.TELEGRAM_DEFAULT_CHAT_ID
    if not chat_id:
        return NotificationSendResult("FAILED", "Telegram chat_id is not configured.")

    text = f"*{subject}*\n\n{message}"
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = request.Request(url, data=payload, method="POST")
    try:
        with request.urlopen(req, timeout=settings.TELEGRAM_TIMEOUT_SECONDS) as resp:  # noqa: S310 - fixed Telegram API endpoint
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            if data.get("ok") is True:
                return NotificationSendResult("SENT")
            return NotificationSendResult("FAILED", body[:1000])
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return NotificationSendResult("FAILED", body[:1000] or str(exc))
    except Exception as exc:  # noqa: BLE001
        return NotificationSendResult("FAILED", str(exc))


def _dispatch(channel: str, *, recipient: str, subject: str, message: str) -> NotificationSendResult:
    if channel == "IN_APP":
        return NotificationSendResult("SENT")
    if channel == "EMAIL":
        return _send_email(recipient=recipient, subject=subject, message=message)
    if channel == "TELEGRAM":
        return _send_telegram(recipient=recipient, subject=subject, message=message)
    return NotificationSendResult("FAILED", f"Unsupported channel: {channel}")


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
    channel = _normalize_channel(channel)
    event_type = event_type.upper().strip()

    result = _dispatch(channel, recipient=recipient, subject=subject, message=message)
    log = NotificationLog(
        event_type=event_type,
        channel=channel,
        recipient=recipient,
        subject=subject,
        message=message,
        status=result.status,
        related_profile_id=related_profile_id,
        error_message=result.error_message,
        sent_at=datetime.utcnow() if result.status == "SENT" else None,
        created_by=created_by,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_notification_runtime_status() -> dict:
    return {
        "dry_run": settings.NOTIFICATION_DRY_RUN,
        "channels": {
            "IN_APP": {"enabled": True, "configured": True},
            "EMAIL": {
                "enabled": settings.SMTP_ENABLED,
                "configured": bool(settings.SMTP_HOST and settings.SMTP_FROM_EMAIL),
                "host": settings.SMTP_HOST,
                "port": settings.SMTP_PORT,
                "from_email": settings.SMTP_FROM_EMAIL,
                "use_tls": settings.SMTP_USE_TLS,
            },
            "TELEGRAM": {
                "enabled": settings.TELEGRAM_ENABLED,
                "configured": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID),
                "default_chat_id_configured": bool(settings.TELEGRAM_DEFAULT_CHAT_ID),
            },
        },
    }
