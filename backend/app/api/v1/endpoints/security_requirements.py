from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.security_requirement import SecurityRequirement
from app.schemas.common import Page
from app.schemas.security_requirement import SecurityRequirementCreate, SecurityRequirementRead, SecurityRequirementUpdate

router = APIRouter()


@router.get("", response_model=Page[SecurityRequirementRead])
def list_security_requirements(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    group_name: str | None = Query(default=None),
    category: str | None = Query(default=None),
    required_level: int | None = Query(default=None, ge=1, le=5),
    max_level: int | None = Query(default=None, ge=1, le=5),
    is_mandatory: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=300),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(SecurityRequirement)
    count_stmt = select(func.count()).select_from(SecurityRequirement)
    filters = []
    if q:
        filters.append((SecurityRequirement.code.ilike(f"%{q}%")) | (SecurityRequirement.title.ilike(f"%{q}%")))
    if group_name:
        filters.append(SecurityRequirement.group_name == group_name)
    if category:
        filters.append(SecurityRequirement.category == category)
    if required_level:
        filters.append(SecurityRequirement.required_level == required_level)
    if max_level:
        filters.append(SecurityRequirement.required_level <= max_level)
    if is_mandatory is not None:
        filters.append(SecurityRequirement.is_mandatory == is_mandatory)
    for condition in filters:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(SecurityRequirement.required_level, SecurityRequirement.group_name, SecurityRequirement.sort_order, SecurityRequirement.code)
        .limit(limit)
        .offset(offset)
    ).all()
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/by-level/{level}", response_model=list[SecurityRequirementRead])
def get_requirements_by_level(level: int, db: Session = Depends(get_db)):
    if level < 1 or level > 5:
        raise HTTPException(status_code=400, detail="level must be from 1 to 5")
    return db.scalars(
        select(SecurityRequirement)
        .where(SecurityRequirement.required_level <= level)
        .order_by(SecurityRequirement.required_level, SecurityRequirement.group_name, SecurityRequirement.sort_order, SecurityRequirement.code)
    ).all()


@router.post("", response_model=SecurityRequirementRead, status_code=status.HTTP_201_CREATED)
def create_security_requirement(
    payload: SecurityRequirementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = SecurityRequirement(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Requirement code already exists") from exc
    db.refresh(item)
    return item


@router.get("/{requirement_id}", response_model=SecurityRequirementRead)
def get_security_requirement(requirement_id: int, db: Session = Depends(get_db)):
    item = db.get(SecurityRequirement, requirement_id)
    if not item:
        raise HTTPException(status_code=404, detail="Security requirement not found")
    return item


@router.put("/{requirement_id}", response_model=SecurityRequirementRead)
def update_security_requirement(
    requirement_id: int,
    payload: SecurityRequirementUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = db.get(SecurityRequirement, requirement_id)
    if not item:
        raise HTTPException(status_code=404, detail="Security requirement not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Requirement code already exists") from exc
    db.refresh(item)
    return item


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_security_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    item = db.get(SecurityRequirement, requirement_id)
    if not item:
        raise HTTPException(status_code=404, detail="Security requirement not found")
    db.delete(item)
    db.commit()
    return None
