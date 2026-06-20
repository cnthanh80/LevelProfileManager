from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.compliance_automation import ComplianceAutomationFinding, ComplianceAutomationRule, ComplianceAutomationRun
from app.models.user import User
from app.schemas.common import Page
from app.schemas.compliance_automation import (
    ComplianceAutomationDashboard,
    ComplianceAutomationFindingRead,
    ComplianceAutomationRuleCreate,
    ComplianceAutomationRuleRead,
    ComplianceAutomationRunRead,
    ComplianceAutomationRunRequest,
    ComplianceAutomationRunResult,
)
from app.services.compliance_automation_service import automation_dashboard, run_compliance_automation, seed_default_automation_rules

router = APIRouter()


@router.get("/dashboard/compliance-automation", response_model=ComplianceAutomationDashboard)
def get_compliance_automation_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return automation_dashboard(db)


@router.post("/compliance-automation/rules/seed-defaults")
def seed_rules(db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    return seed_default_automation_rules(db)


@router.get("/compliance-automation/rules", response_model=Page[ComplianceAutomationRuleRead])
def list_rules(
    enabled: bool | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if enabled is not None:
        filters.append(ComplianceAutomationRule.is_enabled == enabled)
    stmt = select(ComplianceAutomationRule)
    count_stmt = select(func.count(ComplianceAutomationRule.id))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(ComplianceAutomationRule.rule_code).limit(limit).offset(offset)).all()
    return Page[ComplianceAutomationRuleRead](items=items, total=total, limit=limit, offset=offset)


@router.post("/compliance-automation/rules", response_model=ComplianceAutomationRuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(payload: ComplianceAutomationRuleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER"))):
    data = payload.model_dump()
    for key in ["rule_code", "rule_type", "severity"]:
        data[key] = data[key].upper()
    item = ComplianceAutomationRule(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/compliance-automation/run", response_model=ComplianceAutomationRunResult)
def run_automation(payload: ComplianceAutomationRunRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER"))):
    return run_compliance_automation(db, profile_id=payload.profile_id, scope=payload.scope, created_by=current_user.id)


@router.get("/compliance-automation/runs", response_model=Page[ComplianceAutomationRunRead])
def list_runs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(select(func.count(ComplianceAutomationRun.id))) or 0
    items = db.scalars(select(ComplianceAutomationRun).order_by(ComplianceAutomationRun.id.desc()).limit(limit).offset(offset)).all()
    return Page[ComplianceAutomationRunRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/compliance-automation/findings", response_model=Page[ComplianceAutomationFindingRead])
def list_findings(
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
        filters.append(ComplianceAutomationFinding.severity == severity.upper())
    if status_filter:
        filters.append(ComplianceAutomationFinding.status == status_filter.upper())
    if profile_id:
        filters.append(ComplianceAutomationFinding.profile_id == profile_id)
    stmt = select(ComplianceAutomationFinding)
    count_stmt = select(func.count(ComplianceAutomationFinding.id))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(ComplianceAutomationFinding.id.desc()).limit(limit).offset(offset)).all()
    return Page[ComplianceAutomationFindingRead](items=items, total=total, limit=limit, offset=offset)
