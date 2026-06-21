from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.schemas.common import Page
from app.schemas.level_profile import LevelProfileCreate, LevelProfileRead, LevelProfileUpdate

router = APIRouter()


@router.get("", response_model=Page[LevelProfileRead])
def list_level_profiles(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    information_system_id: int | None = Query(default=None),
    proposed_level: int | None = Query(default=None, ge=1, le=5),
    status_value: str | None = Query(default=None, alias="status"),
    include_deleted: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(LevelProfile)
    count_stmt = select(func.count()).select_from(LevelProfile)
    filters = []
    if not include_deleted:
        filters.append(LevelProfile.is_deleted == False)

    if q:
        filters.append(LevelProfile.profile_code.ilike(f"%{q}%"))
    if information_system_id:
        filters.append(LevelProfile.information_system_id == information_system_id)
    if proposed_level:
        filters.append(LevelProfile.proposed_level == proposed_level)
    if status_value:
        filters.append(LevelProfile.status == status_value)

    for condition in filters:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(LevelProfile.id.desc()).limit(limit).offset(offset)).all()
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=LevelProfileRead, status_code=status.HTTP_201_CREATED)
def create_level_profile(payload: LevelProfileCreate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    if db.get(InformationSystem, payload.information_system_id) is None:
        raise HTTPException(status_code=400, detail="information_system_id does not exist")
    item = LevelProfile(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Profile code already exists") from exc
    db.refresh(item)
    return item


@router.get("/{profile_id}", response_model=LevelProfileRead)
def get_level_profile(profile_id: int, db: Session = Depends(get_db)):
    item = db.get(LevelProfile, profile_id)
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Level profile not found")
    return item


@router.put("/{profile_id}", response_model=LevelProfileRead)
def update_level_profile(profile_id: int, payload: LevelProfileUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(LevelProfile, profile_id)
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Level profile not found")
    data = payload.model_dump(exclude_unset=True)
    if "information_system_id" in data and db.get(InformationSystem, data["information_system_id"]) is None:
        raise HTTPException(status_code=400, detail="information_system_id does not exist")
    for key, value in data.items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Profile code already exists") from exc
    db.refresh(item)
    return item


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_level_profile(profile_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(LevelProfile, profile_id)
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Level profile not found")
    if item.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Only DRAFT level profiles can be archived")

    # Soft delete instead of hard delete to preserve workflow history, audit logs, checklist, evidence, signatures and reports.
    item.is_deleted = True
    item.deleted_at = datetime.now(timezone.utc)
    item.deleted_by = getattr(current_user, "id", None)
    item.status = "ARCHIVED"
    db.commit()
    return None


@router.post("/{profile_id}/restore", response_model=LevelProfileRead)
def restore_level_profile(profile_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles("ADMIN"))):
    item = db.get(LevelProfile, profile_id)
    if not item:
        raise HTTPException(status_code=404, detail="Level profile not found")
    if not item.is_deleted:
        return item
    item.is_deleted = False
    item.deleted_at = None
    item.deleted_by = None
    item.status = "DRAFT"
    db.commit()
    db.refresh(item)
    return item
