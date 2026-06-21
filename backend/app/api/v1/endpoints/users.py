from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserRead, UserResetPasswordRequest, UserUpdate
from app.schemas.common import Page

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


@router.get("", response_model=Page[UserRead])
def list_users(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    role_id: int | None = Query(default=None),
    organization_id: int | None = Query(default=None),
    active_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(User)
    count_stmt = select(func.count()).select_from(User)
    conditions = []
    if q:
        pattern = f"%{q}%"
        conditions.append((User.username.ilike(pattern)) | (User.full_name.ilike(pattern)) | (User.email.ilike(pattern)))
    if role_id is not None:
        conditions.append(User.role_id == role_id)
    if organization_id is not None:
        conditions.append(User.organization_id == organization_id)
    if active_only:
        conditions.append(User.is_active.is_(True))
    for cond in conditions:
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(User.id.desc()).limit(limit).offset(offset)).all()
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role_id=payload.role_id,
        organization_id=payload.organization_id,
        is_active=payload.is_active,
        auth_provider=payload.auth_provider,
        external_id=payload.external_id,
        is_local_auth_allowed=payload.is_local_auth_allowed,
        failed_login_count=payload.failed_login_count,
        locked_until=payload.locked_until,
        last_login_at=payload.last_login_at,
        must_change_password=payload.must_change_password,
        password_changed_at=datetime.now(timezone.utc),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists") from exc
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    if password:
        user.hashed_password = get_password_hash(password)
        user.password_changed_at = datetime.now(timezone.utc)
    for key, value in data.items():
        setattr(user, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists") from exc
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Default admin user cannot be deleted")
    db.delete(user)
    db.commit()
    return None


@router.post("/{user_id}/lock", response_model=UserRead)
def lock_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Default admin user cannot be locked")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/unlock", response_model=UserRead)
def unlock_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/reset-password", response_model=UserRead)
def reset_user_password(user_id: int, payload: UserResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(payload.new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    user.must_change_password = payload.must_change_password
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()
    db.refresh(user)
    return user
