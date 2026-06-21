from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.cmdb import CmdbApplication, CmdbAsset, CmdbDatabase, CmdbNetworkDevice, CmdbRelationship
from app.models.user import User
from app.schemas.cmdb import (
    CmdbApplicationCreate,
    CmdbApplicationRead,
    CmdbApplicationUpdate,
    CmdbAssetCreate,
    CmdbAssetRead,
    CmdbAssetUpdate,
    CmdbDashboard,
    CmdbDatabaseCreate,
    CmdbDatabaseRead,
    CmdbDatabaseUpdate,
    CmdbImportPayload,
    CmdbNetworkDeviceCreate,
    CmdbNetworkDeviceRead,
    CmdbNetworkDeviceUpdate,
    CmdbProfileInventory,
    CmdbRelationshipCreate,
    CmdbRelationshipRead,
    CmdbSyncResult,
)
from app.schemas.common import Page
from app.services.cmdb_service import cmdb_dashboard, import_assets, profile_inventory, sync_profile_from_cmdb

router = APIRouter()


def _page(db: Session, model, limit: int, offset: int, filters=None, order_by=None):
    stmt = select(model)
    count_stmt = select(func.count(model.id))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    if order_by is not None:
        stmt = stmt.order_by(order_by)
    else:
        stmt = stmt.order_by(model.id.desc())
    return db.scalars(stmt.limit(limit).offset(offset)).all(), total


@router.get("/cmdb/dashboard", response_model=CmdbDashboard)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return cmdb_dashboard(db)


@router.post("/cmdb/import/assets")
def import_cmdb_assets(
    payload: CmdbImportPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return import_assets(db, payload.model_dump())


@router.get("/profiles/{profile_id}/cmdb-inventory", response_model=CmdbProfileInventory)
def get_profile_inventory(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return profile_inventory(db, profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/cmdb-sync", response_model=CmdbSyncResult)
def sync_profile_cmdb(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    try:
        return sync_profile_from_cmdb(db, profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/cmdb-assets", response_model=Page[CmdbAssetRead])
def list_assets(
    information_system_id: int | None = None,
    asset_type: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if information_system_id:
        filters.append(CmdbAsset.information_system_id == information_system_id)
    if asset_type:
        filters.append(CmdbAsset.asset_type == asset_type.upper())
    if status_filter:
        filters.append(CmdbAsset.status == status_filter.upper())
    items, total = _page(db, CmdbAsset, limit, offset, filters, CmdbAsset.asset_name)
    return Page[CmdbAssetRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/cmdb-assets", response_model=CmdbAssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: CmdbAssetCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    if db.scalar(select(CmdbAsset).where(CmdbAsset.asset_code == payload.asset_code)):
        raise HTTPException(status_code=409, detail="Asset code already exists")
    data = payload.model_dump()
    for key in ["asset_type", "environment", "criticality", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    item = CmdbAsset(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/cmdb-assets/{asset_id}", response_model=CmdbAssetRead)
def update_asset(asset_id: int, payload: CmdbAssetUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbAsset, asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    data = payload.model_dump(exclude_unset=True)
    for key in ["asset_type", "environment", "criticality", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/cmdb-assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbAsset, asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/cmdb-applications", response_model=Page[CmdbApplicationRead])
def list_applications(
    information_system_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [CmdbApplication.information_system_id == information_system_id] if information_system_id else []
    items, total = _page(db, CmdbApplication, limit, offset, filters, CmdbApplication.app_name)
    return Page[CmdbApplicationRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/cmdb-applications", response_model=CmdbApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: CmdbApplicationCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    if db.scalar(select(CmdbApplication).where(CmdbApplication.app_code == payload.app_code)):
        raise HTTPException(status_code=409, detail="Application code already exists")
    data = payload.model_dump()
    for key in ["app_type", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    item = CmdbApplication(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/cmdb-applications/{application_id}", response_model=CmdbApplicationRead)
def update_application(application_id: int, payload: CmdbApplicationUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbApplication, application_id)
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    data = payload.model_dump(exclude_unset=True)
    for key in ["app_type", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/cmdb-applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbApplication, application_id)
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/cmdb-databases", response_model=Page[CmdbDatabaseRead])
def list_databases(
    information_system_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [CmdbDatabase.information_system_id == information_system_id] if information_system_id else []
    items, total = _page(db, CmdbDatabase, limit, offset, filters, CmdbDatabase.db_name)
    return Page[CmdbDatabaseRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/cmdb-databases", response_model=CmdbDatabaseRead, status_code=status.HTTP_201_CREATED)
def create_database(payload: CmdbDatabaseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    if db.scalar(select(CmdbDatabase).where(CmdbDatabase.db_code == payload.db_code)):
        raise HTTPException(status_code=409, detail="Database code already exists")
    data = payload.model_dump()
    for key in ["db_type", "data_classification", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    item = CmdbDatabase(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/cmdb-databases/{database_id}", response_model=CmdbDatabaseRead)
def update_database(database_id: int, payload: CmdbDatabaseUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbDatabase, database_id)
    if not item:
        raise HTTPException(status_code=404, detail="Database not found")
    data = payload.model_dump(exclude_unset=True)
    for key in ["db_type", "data_classification", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/cmdb-databases/{database_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_database(database_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbDatabase, database_id)
    if not item:
        raise HTTPException(status_code=404, detail="Database not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/cmdb-network-devices", response_model=Page[CmdbNetworkDeviceRead])
def list_network_devices(
    information_system_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [CmdbNetworkDevice.information_system_id == information_system_id] if information_system_id else []
    items, total = _page(db, CmdbNetworkDevice, limit, offset, filters, CmdbNetworkDevice.device_name)
    return Page[CmdbNetworkDeviceRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/cmdb-network-devices", response_model=CmdbNetworkDeviceRead, status_code=status.HTTP_201_CREATED)
def create_network_device(payload: CmdbNetworkDeviceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    if db.scalar(select(CmdbNetworkDevice).where(CmdbNetworkDevice.device_code == payload.device_code)):
        raise HTTPException(status_code=409, detail="Network device code already exists")
    data = payload.model_dump()
    for key in ["device_type", "zone", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    item = CmdbNetworkDevice(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/cmdb-network-devices/{device_id}", response_model=CmdbNetworkDeviceRead)
def update_network_device(device_id: int, payload: CmdbNetworkDeviceUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbNetworkDevice, device_id)
    if not item:
        raise HTTPException(status_code=404, detail="Network device not found")
    data = payload.model_dump(exclude_unset=True)
    for key in ["device_type", "zone", "status"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/cmdb-network-devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_network_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(CmdbNetworkDevice, device_id)
    if not item:
        raise HTTPException(status_code=404, detail="Network device not found")
    db.delete(item)
    db.commit()
    return None


@router.post("/cmdb-relationships", response_model=CmdbRelationshipRead, status_code=status.HTTP_201_CREATED)
def create_relationship(payload: CmdbRelationshipCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    data = payload.model_dump()
    for key in ["source_type", "target_type", "relationship_type"]:
        data[key] = data[key].upper()
    item = CmdbRelationship(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
