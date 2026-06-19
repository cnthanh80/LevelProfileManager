from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, IdentityProviderStatus, LdapLoginRequest, RoleRead, SsoLoginHint, Token, UserRead

router = APIRouter()


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form_data.username))
    if not user or not user.is_local_auth_allowed or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    role = db.get(Role, user.role_id) if user.role_id else None
    access_token = create_access_token(
        subject=user.username,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"role": role.code if role else None, "user_id": user.id},
    )
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/identity-provider/status", response_model=IdentityProviderStatus)
def identity_provider_status(current_user: User = Depends(get_current_user)):
    return IdentityProviderStatus(
        local_login_enabled=True,
        ldap_enabled=settings.LDAP_ENABLED,
        ldap_dry_run=settings.LDAP_DRY_RUN,
        sso_enabled=settings.SSO_ENABLED,
        sso_provider_name=settings.SSO_PROVIDER_NAME,
        sso_login_url=settings.SSO_LOGIN_URL,
    )


@router.get("/sso/login-hint", response_model=SsoLoginHint)
def sso_login_hint():
    if not settings.SSO_ENABLED:
        return SsoLoginHint(
            enabled=False,
            provider_name=settings.SSO_PROVIDER_NAME,
            login_url=None,
            message="SSO is not enabled. Use local JWT login for this environment.",
        )
    return SsoLoginHint(
        enabled=True,
        provider_name=settings.SSO_PROVIDER_NAME,
        login_url=settings.SSO_LOGIN_URL,
        message="Redirect the browser to login_url and exchange the identity assertion in a future production adapter.",
    )


@router.post("/ldap-login", response_model=Token)
def ldap_login(payload: LdapLoginRequest, db: Session = Depends(get_db)):
    if not settings.LDAP_ENABLED and not settings.LDAP_DRY_RUN:
        raise HTTPException(status_code=400, detail="LDAP login is disabled")

    # Foundation implementation: dry-run mode validates against local users so the
    # deployment can be tested without connecting to Active Directory/LDAP yet.
    # A production adapter can replace this block with real LDAP bind/search.
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect LDAP username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    role = db.get(Role, user.role_id) if user.role_id else None
    access_token = create_access_token(
        subject=user.username,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"role": role.code if role else None, "user_id": user.id, "auth_provider": "LDAP_DRY_RUN"},
    )
    return Token(access_token=access_token)


@router.get("/roles", response_model=list[RoleRead])
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(Role).order_by(Role.id)).all()


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"status": "ok"}
