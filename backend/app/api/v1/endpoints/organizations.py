from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.organization import Organization
from app.schemas.common import Page
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationScopeSummary, OrganizationTreeNode, OrganizationUpdate
from app.services.organization_service import build_org_tree, compute_org_level_path, organization_scope_summary

router = APIRouter()


def _validate_parent(db: Session, org_id: int | None, parent_id: int | None) -> None:
    if parent_id is None:
        return
    if org_id is not None and org_id == parent_id:
        raise HTTPException(status_code=400, detail="Organization cannot be its own parent")
    parent = db.get(Organization, parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent organization not found")
    if org_id is not None and parent.path and db.get(Organization, org_id):
        current = db.get(Organization, org_id)
        if current and current.path and parent.path.startswith(current.path):
            raise HTTPException(status_code=400, detail="Parent cannot be a descendant organization")


@router.get("", response_model=Page[OrganizationRead])
def list_organizations(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    parent_id: int | None = Query(default=None),
    active_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(Organization)
    count_stmt = select(func.count()).select_from(Organization)
    if q:
        pattern = f"%{q}%"
        condition = (Organization.code.ilike(pattern)) | (Organization.name.ilike(pattern)) | (Organization.path.ilike(pattern))
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    if parent_id is not None:
        stmt = stmt.where(Organization.parent_id == parent_id)
        count_stmt = count_stmt.where(Organization.parent_id == parent_id)
    if active_only:
        stmt = stmt.where(Organization.is_active.is_(True))
        count_stmt = count_stmt.where(Organization.is_active.is_(True))

    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(Organization.level.asc(), Organization.name.asc()).limit(limit).offset(offset)).all()
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/tree", response_model=list[OrganizationTreeNode])
def organization_tree(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return build_org_tree(db)


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    _validate_parent(db, None, payload.parent_id)
    item = Organization(**payload.model_dump())
    compute_org_level_path(db, item)
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


@router.get("/{organization_id}/scope-summary", response_model=OrganizationScopeSummary)
def get_organization_scope_summary(organization_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    summary = organization_scope_summary(db, organization_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Organization not found")
    return summary


@router.put("/{organization_id}", response_model=OrganizationRead)
def update_organization(organization_id: int, payload: OrganizationUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(Organization, organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Organization not found")
    data = payload.model_dump(exclude_unset=True)
    parent_id = data.get("parent_id", item.parent_id)
    _validate_parent(db, organization_id, parent_id)
    for key, value in data.items():
        setattr(item, key, value)
    compute_org_level_path(db, item)
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
