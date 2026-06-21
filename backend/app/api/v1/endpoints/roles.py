from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import RoleCreate, RoleRead, RoleUpdate
from app.schemas.common import Page

router = APIRouter()


@router.get("", response_model=Page[RoleRead])
def list_roles(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
):
    stmt = select(Role)
    count_stmt = select(func.count()).select_from(Role)
    if q:
        pattern = f"%{q}%"
        cond = (Role.code.ilike(pattern)) | (Role.name.ilike(pattern)) | (Role.description.ilike(pattern))
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(Role.id.asc()).limit(limit).offset(offset)).all()
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("ADMIN"))])
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    role = Role(code=payload.code.upper(), name=payload.name, description=payload.description)
    db.add(role)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Role code already exists") from exc
    db.refresh(role)
    return role


@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=RoleRead, dependencies=[Depends(require_roles("ADMIN"))])
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    data = payload.model_dump(exclude_unset=True)
    if "code" in data and data["code"]:
        data["code"] = data["code"].upper()
    for key, value in data.items():
        setattr(role, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Role code already exists") from exc
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("ADMIN"))])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    users_count = db.scalar(select(func.count()).select_from(User).where(User.role_id == role_id)) or 0
    if users_count:
        raise HTTPException(status_code=400, detail="Role is assigned to users and cannot be deleted")
    if role.code == "ADMIN":
        raise HTTPException(status_code=400, detail="ADMIN role cannot be deleted")
    db.delete(role)
    db.commit()
    return None
