from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.config import settings
from app.db.session import get_db
from app.models.security_event import SecurityEvent
from app.models.user import User
from app.schemas.auth import UserRead
from app.schemas.security_hardening import (
    PasswordPolicyStatus,
    PasswordValidationRequest,
    PasswordValidationResult,
    SecurityEventCreate,
    SecurityEventRead,
    SecuritySummary,
)
from app.services.security_hardening_service import (
    create_security_event,
    get_security_summary,
    unlock_user,
    validate_password_policy,
)

router = APIRouter()


@router.get("/security/password-policy", response_model=PasswordPolicyStatus)
def password_policy(current_user: User = Depends(get_current_user)):
    return PasswordPolicyStatus(
        min_length=settings.PASSWORD_MIN_LENGTH,
        require_uppercase=settings.PASSWORD_REQUIRE_UPPERCASE,
        require_lowercase=settings.PASSWORD_REQUIRE_LOWERCASE,
        require_digit=settings.PASSWORD_REQUIRE_DIGIT,
        require_special=settings.PASSWORD_REQUIRE_SPECIAL,
        lockout_enabled=settings.ACCOUNT_LOCKOUT_ENABLED,
        lockout_threshold=settings.ACCOUNT_LOCKOUT_THRESHOLD,
        lockout_minutes=settings.ACCOUNT_LOCKOUT_MINUTES,
    )


@router.post("/security/password-policy/validate", response_model=PasswordValidationResult)
def validate_password(payload: PasswordValidationRequest, current_user: User = Depends(get_current_user)):
    valid, score, issues = validate_password_policy(payload.password)
    return PasswordValidationResult(valid=valid, score=score, issues=issues)


@router.get("/security/events", response_model=list[SecurityEventRead])
def list_security_events(
    event_type: str | None = None,
    severity: str | None = None,
    username: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    stmt = select(SecurityEvent).order_by(SecurityEvent.id.desc())
    if event_type:
        stmt = stmt.where(SecurityEvent.event_type == event_type)
    if severity:
        stmt = stmt.where(SecurityEvent.severity == severity)
    if username:
        stmt = stmt.where(SecurityEvent.username == username)
    return db.scalars(stmt.offset(offset).limit(min(limit, 200))).all()


@router.post("/security/events", response_model=SecurityEventRead)
def create_manual_security_event(
    payload: SecurityEventCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return create_security_event(
        db,
        event_type=payload.event_type,
        severity=payload.severity,
        username=payload.username or current_user.username,
        user_id=payload.user_id or current_user.id,
        ip_address=payload.ip_address or request.client.host if request.client else None,
        user_agent=payload.user_agent or request.headers.get("user-agent"),
        detail=payload.detail,
    )


@router.get("/security/summary", response_model=SecuritySummary)
def security_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return get_security_summary(db)


@router.post("/users/{user_id}/security/unlock", response_model=UserRead)
def unlock_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return unlock_user(db, user, actor_username=current_user.username)
