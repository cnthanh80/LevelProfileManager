from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.risk_register import RiskRegisterItem, SlaPolicy
from app.models.user import User
from app.schemas.common import Page
from app.schemas.risk_register import (
    RiskRegisterCreate,
    RiskRegisterRead,
    RiskRegisterSummary,
    RiskRegisterUpdate,
    SlaPolicyCreate,
    SlaPolicyRead,
    SlaPolicyUpdate,
    SlaSummary,
)
from app.services.risk_register_service import get_risk_summary, get_sla_summary, normalize_risk, seed_default_sla_policies

router = APIRouter()


@router.get("/risk-registers/summary", response_model=RiskRegisterSummary)
def risk_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_risk_summary(db)


@router.get("/risk-registers", response_model=Page[RiskRegisterRead])
def list_risks(
    profile_id: int | None = None,
    risk_level: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(RiskRegisterItem)
    count_stmt = select(func.count(RiskRegisterItem.id))
    filters = []
    if profile_id:
        filters.append(RiskRegisterItem.profile_id == profile_id)
    if risk_level:
        filters.append(RiskRegisterItem.risk_level == risk_level.upper())
    if status_filter:
        filters.append(RiskRegisterItem.status == status_filter.upper())
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(RiskRegisterItem.risk_score.desc(), RiskRegisterItem.id.desc()).limit(limit).offset(offset)).all()
    return Page[RiskRegisterRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/risk-registers", response_model=RiskRegisterRead, status_code=status.HTTP_201_CREATED)
def create_risk(
    payload: RiskRegisterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    existing = db.scalar(select(RiskRegisterItem).where(RiskRegisterItem.risk_code == payload.risk_code))
    if existing:
        raise HTTPException(status_code=409, detail="Risk code already exists")
    item = RiskRegisterItem(**payload.model_dump(), created_by=current_user.id)
    normalize_risk(item)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/risk-registers/{risk_id}", response_model=RiskRegisterRead)
def get_risk(risk_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(RiskRegisterItem, risk_id)
    if not item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    return item


@router.put("/risk-registers/{risk_id}", response_model=RiskRegisterRead)
def update_risk(
    risk_id: int,
    payload: RiskRegisterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    item = db.get(RiskRegisterItem, risk_id)
    if not item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key in {"category", "status"} and isinstance(value, str):
            value = value.upper()
        setattr(item, key, value)
    normalize_risk(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/risk-registers/{risk_id}/close", response_model=RiskRegisterRead)
def close_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    item = db.get(RiskRegisterItem, risk_id)
    if not item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    item.status = "CLOSED"
    db.commit()
    db.refresh(item)
    return item


@router.get("/sla/policies", response_model=Page[SlaPolicyRead])
def list_sla_policies(
    active_only: bool = True,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(SlaPolicy)
    count_stmt = select(func.count(SlaPolicy.id))
    if active_only:
        stmt = stmt.where(SlaPolicy.is_active == "Y")
        count_stmt = count_stmt.where(SlaPolicy.is_active == "Y")
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(SlaPolicy.id).limit(limit).offset(offset)).all()
    return Page[SlaPolicyRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/sla/policies", response_model=SlaPolicyRead, status_code=status.HTTP_201_CREATED)
def create_sla_policy(
    payload: SlaPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    existing = db.scalar(select(SlaPolicy).where(SlaPolicy.code == payload.code))
    if existing:
        raise HTTPException(status_code=409, detail="SLA policy code already exists")
    data = payload.model_dump()
    for key in ["target_type", "workflow_status", "severity", "is_active"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].upper()
    item = SlaPolicy(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/sla/policies/{policy_id}", response_model=SlaPolicyRead)
def update_sla_policy(
    policy_id: int,
    payload: SlaPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    item = db.get(SlaPolicy, policy_id)
    if not item:
        raise HTTPException(status_code=404, detail="SLA policy not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key in {"target_type", "workflow_status", "severity", "is_active"} and isinstance(value, str):
            value = value.upper()
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.post("/sla/policies/seed-defaults")
def seed_sla_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER")),
):
    return {"status": "ok", "created": seed_default_sla_policies(db)}


@router.get("/sla/summary", response_model=SlaSummary)
def sla_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_sla_summary(db)
