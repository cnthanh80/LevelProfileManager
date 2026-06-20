from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.siem_integration import SiemConnector, SiemCorrelationRule, SiemEvent
from app.models.user import User
from app.schemas.common import Page
from app.schemas.siem_integration import (
    SiemConnectorCreate,
    SiemConnectorRead,
    SiemConnectorUpdate,
    SiemDashboard,
    SiemEventIngest,
    SiemEventRead,
    SiemRuleCreate,
    SiemRuleRead,
    SiemStatus,
)
from app.services.siem_service import (
    correlation_summary,
    ingest_event,
    ingest_from_audit,
    ingest_from_security_events,
    seed_default_connectors,
    seed_default_rules,
    siem_dashboard,
    siem_status,
)

router = APIRouter()


def _page(db: Session, model, limit: int, offset: int, filters=None, order_by=None):
    stmt = select(model)
    count_stmt = select(func.count(model.id))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    stmt = stmt.order_by(order_by if order_by is not None else model.id.desc())
    return db.scalars(stmt.limit(limit).offset(offset)).all(), total


@router.get("/siem/status", response_model=SiemStatus)
def get_siem_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return siem_status(db)


@router.get("/dashboard/siem", response_model=SiemDashboard)
def get_siem_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return siem_dashboard(db)


@router.get("/siem/correlation/summary")
def get_correlation_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return correlation_summary(db)


@router.post("/siem/connectors/seed-defaults")
def seed_connectors(db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    return seed_default_connectors(db)


@router.get("/siem/connectors", response_model=Page[SiemConnectorRead])
def list_connectors(
    connector_type: str | None = None,
    enabled: bool | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if connector_type:
        filters.append(SiemConnector.connector_type == connector_type.upper())
    if enabled is not None:
        filters.append(SiemConnector.is_enabled == enabled)
    items, total = _page(db, SiemConnector, limit, offset, filters, SiemConnector.connector_name)
    return Page[SiemConnectorRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/siem/connectors", response_model=SiemConnectorRead, status_code=status.HTTP_201_CREATED)
def create_connector(payload: SiemConnectorCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    if db.scalar(select(SiemConnector).where(SiemConnector.connector_code == payload.connector_code)):
        raise HTTPException(status_code=409, detail="Connector code already exists")
    data = payload.model_dump()
    for key in ["connector_type", "auth_type"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    item = SiemConnector(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/siem/connectors/{connector_id}", response_model=SiemConnectorRead)
def update_connector(connector_id: int, payload: SiemConnectorUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    item = db.get(SiemConnector, connector_id)
    if not item:
        raise HTTPException(status_code=404, detail="Connector not found")
    data = payload.model_dump(exclude_unset=True)
    for key in ["connector_type", "auth_type"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.post("/siem/events/ingest", response_model=SiemEventRead, status_code=status.HTTP_201_CREATED)
def ingest_siem_event(payload: SiemEventIngest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    return ingest_event(db, payload.model_dump())


@router.post("/siem/events/ingest-audit")
def ingest_audit_events(limit: int = Query(default=20, ge=1, le=200), db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    return ingest_from_audit(db, limit)


@router.post("/siem/events/ingest-security")
def ingest_security_events(limit: int = Query(default=20, ge=1, le=200), db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    return ingest_from_security_events(db, limit)


@router.get("/siem/events", response_model=Page[SiemEventRead])
def list_events(
    severity: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    profile_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if severity:
        filters.append(SiemEvent.severity == severity.upper())
    if status_filter:
        filters.append(SiemEvent.status == status_filter.upper())
    if profile_id:
        filters.append(SiemEvent.profile_id == profile_id)
    items, total = _page(db, SiemEvent, limit, offset, filters, SiemEvent.id.desc())
    return Page[SiemEventRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/siem/rules/seed-defaults")
def seed_rules(db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    return seed_default_rules(db)


@router.get("/siem/rules", response_model=Page[SiemRuleRead])
def list_rules(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = _page(db, SiemCorrelationRule, limit, offset, [], SiemCorrelationRule.rule_code)
    return Page[SiemRuleRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/siem/rules", response_model=SiemRuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(payload: SiemRuleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    if db.scalar(select(SiemCorrelationRule).where(SiemCorrelationRule.rule_code == payload.rule_code)):
        raise HTTPException(status_code=409, detail="Rule code already exists")
    data = payload.model_dump()
    for key in ["event_type", "min_severity"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    item = SiemCorrelationRule(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
