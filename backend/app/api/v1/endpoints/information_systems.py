from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.information_system import InformationSystem
from app.models.organization import Organization
from app.schemas.common import Page
from app.schemas.information_system import (
    InformationSystemCreate,
    InformationSystemRead,
    InformationSystemUpdate,
)

router = APIRouter()


def _validate_org(db: Session, org_id: int | None, field_name: str) -> None:
    if org_id is not None and db.get(Organization, org_id) is None:
        raise HTTPException(status_code=400, detail=f"{field_name} does not exist")


@router.get("", response_model=Page[InformationSystemRead])
def list_information_systems(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    proposed_level: int | None = Query(default=None, ge=1, le=5),
    operation_status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(InformationSystem)
    count_stmt = select(func.count()).select_from(InformationSystem)

    filters = []
    if q:
        pattern = f"%{q}%"
        filters.append((InformationSystem.code.ilike(pattern)) | (InformationSystem.name.ilike(pattern)))
    if proposed_level:
        filters.append(InformationSystem.proposed_level == proposed_level)
    if operation_status:
        filters.append(InformationSystem.operation_status == operation_status)

    for condition in filters:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(InformationSystem.id.desc()).limit(limit).offset(offset)).all()
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=InformationSystemRead, status_code=status.HTTP_201_CREATED)
def create_information_system(payload: InformationSystemCreate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER", "OPERATOR"))):
    _validate_org(db, payload.owner_org_id, "owner_org_id")
    _validate_org(db, payload.operator_org_id, "operator_org_id")
    item = InformationSystem(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Information system code already exists") from exc
    db.refresh(item)
    return item


@router.get("/{system_id}", response_model=InformationSystemRead)
def get_information_system(system_id: int, db: Session = Depends(get_db)):
    item = db.get(InformationSystem, system_id)
    if not item:
        raise HTTPException(status_code=404, detail="Information system not found")
    return item


@router.put("/{system_id}", response_model=InformationSystemRead)
def update_information_system(system_id: int, payload: InformationSystemUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER", "OPERATOR"))):
    item = db.get(InformationSystem, system_id)
    if not item:
        raise HTTPException(status_code=404, detail="Information system not found")
    data = payload.model_dump(exclude_unset=True)
    _validate_org(db, data.get("owner_org_id"), "owner_org_id")
    _validate_org(db, data.get("operator_org_id"), "operator_org_id")
    for key, value in data.items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Information system code already exists") from exc
    db.refresh(item)
    return item


@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_information_system(system_id: int, db: Session = Depends(get_db)):
    item = db.get(InformationSystem, system_id)
    if not item:
        raise HTTPException(status_code=404, detail="Information system not found")
    db.delete(item)
    db.commit()
    return None
