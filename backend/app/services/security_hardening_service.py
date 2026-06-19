from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.security_event import SecurityEvent
from app.models.user import User


def validate_password_policy(password: str) -> tuple[bool, int, list[str]]:
    issues: list[str] = []
    score = 0
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        issues.append(f"Mật khẩu phải có tối thiểu {settings.PASSWORD_MIN_LENGTH} ký tự")
    else:
        score += 25
    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        issues.append("Mật khẩu phải có chữ hoa")
    else:
        score += 15
    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        issues.append("Mật khẩu phải có chữ thường")
    else:
        score += 15
    if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        issues.append("Mật khẩu phải có chữ số")
    else:
        score += 20
    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r"[^A-Za-z0-9]", password):
        issues.append("Mật khẩu phải có ký tự đặc biệt")
    else:
        score += 25
    return len(issues) == 0, min(score, 100), issues


def create_security_event(
    db: Session,
    event_type: str,
    severity: str = "INFO",
    username: str | None = None,
    user_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    detail: str | None = None,
) -> SecurityEvent:
    event = SecurityEvent(
        event_type=event_type,
        severity=severity,
        username=username,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        detail=detail,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def is_user_locked(user: User) -> bool:
    if not user.locked_until:
        return False
    now = datetime.now(timezone.utc)
    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    return locked_until > now


def register_failed_login(db: Session, username: str, ip_address: str | None = None, user_agent: str | None = None) -> None:
    user = db.scalar(select(User).where(User.username == username))
    if user:
        user.failed_login_count = (user.failed_login_count or 0) + 1
        if settings.ACCOUNT_LOCKOUT_ENABLED and user.failed_login_count >= settings.ACCOUNT_LOCKOUT_THRESHOLD:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
            create_security_event(db, "ACCOUNT_LOCKED", "HIGH", username=username, user_id=user.id, ip_address=ip_address, user_agent=user_agent, detail="Tài khoản bị khóa tạm thời do đăng nhập sai nhiều lần")
        else:
            create_security_event(db, "LOGIN_FAILED", "MEDIUM", username=username, user_id=user.id, ip_address=ip_address, user_agent=user_agent, detail="Đăng nhập thất bại")
        db.commit()
    else:
        create_security_event(db, "LOGIN_FAILED_UNKNOWN_USER", "MEDIUM", username=username, ip_address=ip_address, user_agent=user_agent, detail="Đăng nhập thất bại với username không tồn tại")


def register_successful_login(db: Session, user: User, ip_address: str | None = None, user_agent: str | None = None) -> None:
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    create_security_event(db, "LOGIN_SUCCESS", "INFO", username=user.username, user_id=user.id, ip_address=ip_address, user_agent=user_agent, detail="Đăng nhập thành công")
    db.commit()


def unlock_user(db: Session, user: User, actor_username: str | None = None) -> User:
    user.failed_login_count = 0
    user.locked_until = None
    db.add(user)
    create_security_event(db, "ACCOUNT_UNLOCKED", "INFO", username=user.username, user_id=user.id, detail=f"Mở khóa bởi {actor_username or 'system'}")
    db.commit()
    db.refresh(user)
    return user


def get_security_summary(db: Session) -> dict:
    total_events = db.scalar(select(func.count(SecurityEvent.id))) or 0
    failed_logins = db.scalar(select(func.count(SecurityEvent.id)).where(SecurityEvent.event_type.in_(["LOGIN_FAILED", "LOGIN_FAILED_UNKNOWN_USER"]))) or 0
    high_severity_events = db.scalar(select(func.count(SecurityEvent.id)).where(SecurityEvent.severity.in_(["HIGH", "CRITICAL"]))) or 0
    now = datetime.now(timezone.utc)
    locked_accounts = db.scalar(select(func.count(User.id)).where(User.locked_until != None, User.locked_until > now)) or 0  # noqa: E711
    last_events = db.scalars(select(SecurityEvent).order_by(SecurityEvent.id.desc()).limit(10)).all()
    return {
        "total_events": total_events,
        "failed_logins": failed_logins,
        "locked_accounts": locked_accounts,
        "high_severity_events": high_severity_events,
        "last_events": last_events,
    }
