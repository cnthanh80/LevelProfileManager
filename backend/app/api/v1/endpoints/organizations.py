from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.organization import Organization
from app.schemas.common import Page
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate

router = APIRouter()


@router.get("", response_model=Page[OrganizationRead])
def list_organizations(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(Organization)
    count_stmt = select(func.count()).select_from(Organization)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where((Organization.code.ilike(pattern)) | (Organization.name.ilike(pattern)))
        count_stmt = count_stmt.where((Organization.code.ilike(pattern)) | (Organization.name.ilike(pattern)))

    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(Organization.id.desc()).limit(limit).offset(offset)).all()
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = Organization(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Organization code already exists") from exc
    db.refresh(item)
    return item


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    item = db.get(Organization, organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Organization not found")
    return item


@router.put("/{organization_id}", response_model=OrganizationRead)
def update_organization(organization_id: int, payload: OrganizationUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(Organization, organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Organization not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Organization code already exists") from exc
    db.refresh(item)
    return item


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(organization_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN"))):
    item = db.get(Organization, organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Organization not found")
    db.delete(item)
    db.commit()
    return None
