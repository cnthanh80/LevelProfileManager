from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except Exception as exc:
        raise credentials_exception from exc

    user = db.scalar(select(User).where(User.username == username))
    if not user or not user.is_active:
        raise credentials_exception
    return user


def get_current_role(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Role | None:
    if user.role_id is None:
        return None
    return db.get(Role, user.role_id)


def require_roles(*allowed_role_codes: str) -> Callable:
    def checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        role = db.get(Role, current_user.role_id) if current_user.role_id else None
        if not role or role.code not in allowed_role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Require one of roles: {', '.join(allowed_role_codes)}",
            )
        return current_user

    return checker


RequireAdmin = Depends(require_roles("ADMIN"))
RequireSecurityOfficer = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))
RequireReviewer = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER"))
RequireApprover = Depends(require_roles("ADMIN", "APPROVER"))

# Backward-compatible alias used by dashboard endpoints.
def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
