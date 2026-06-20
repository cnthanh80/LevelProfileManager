from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.compliance_monitoring import ComplianceMonitoringFinding, ComplianceMonitoringNotification, ComplianceSnapshot
from app.models.user import User
from app.schemas.common import Page
from app.schemas.compliance_monitoring import (
    ComplianceHeatmapItem,
    ComplianceMonitoringDashboard,
    ComplianceMonitoringFindingRead,
    ComplianceMonitoringNotificationRead,
    ComplianceMonitoringRunRequest,
    ComplianceMonitoringRunResult,
    ComplianceMonitoringScoreResult,
    ComplianceSnapshotRead,
    ComplianceTrendPoint,
)
from app.services.compliance_monitoring_service import (
    calculate_profile_monitoring_score,
    latest_heatmap,
    monitoring_dashboard,
    run_continuous_monitoring,
    trend_for_profile,
)

router = APIRouter()


@router.get("/dashboard/compliance-monitoring", response_model=ComplianceMonitoringDashboard)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return monitoring_dashboard(db)


@router.get("/compliance-monitoring/score/{profile_id}", response_model=ComplianceMonitoringScoreResult)
def score(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return calculate_profile_monitoring_score(db, profile_id)


@router.post("/compliance-monitoring/recalculate", response_model=ComplianceMonitoringRunResult)
def recalculate(
    payload: ComplianceMonitoringRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    return run_continuous_monitoring(db, profile_id=payload.profile_id, scope=payload.scope, create_notifications=payload.create_notifications)


@router.get("/compliance-monitoring/snapshots", response_model=Page[ComplianceSnapshotRead])
def snapshots(
    profile_id: int | None = None,
    risk_level: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if profile_id:
        filters.append(ComplianceSnapshot.profile_id == profile_id)
    if risk_level:
        filters.append(ComplianceSnapshot.risk_level == risk_level.upper())
    stmt = select(ComplianceSnapshot)
    count_stmt = select(func.count(ComplianceSnapshot.id))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(ComplianceSnapshot.snapshot_at.desc(), ComplianceSnapshot.id.desc()).limit(limit).offset(offset)).all()
    return Page[ComplianceSnapshotRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/compliance-monitoring/findings", response_model=Page[ComplianceMonitoringFindingRead])
def findings(
    profile_id: int | None = None,
    severity: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if profile_id:
        filters.append(ComplianceMonitoringFinding.profile_id == profile_id)
    if severity:
        filters.append(ComplianceMonitoringFinding.severity == severity.upper())
    if status_filter:
        filters.append(ComplianceMonitoringFinding.status == status_filter.upper())
    stmt = select(ComplianceMonitoringFinding)
    count_stmt = select(func.count(ComplianceMonitoringFinding.id))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(ComplianceMonitoringFinding.id.desc()).limit(limit).offset(offset)).all()
    return Page[ComplianceMonitoringFindingRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/compliance-monitoring/notifications", response_model=Page[ComplianceMonitoringNotificationRead])
def notifications(
    profile_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if profile_id:
        filters.append(ComplianceMonitoringNotification.profile_id == profile_id)
    stmt = select(ComplianceMonitoringNotification)
    count_stmt = select(func.count(ComplianceMonitoringNotification.id))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(ComplianceMonitoringNotification.id.desc()).limit(limit).offset(offset)).all()
    return Page[ComplianceMonitoringNotificationRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/compliance-monitoring/heatmap", response_model=list[ComplianceHeatmapItem])
def heatmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return latest_heatmap(db)


@router.get("/compliance-monitoring/trends/{profile_id}", response_model=list[ComplianceTrendPoint])
def trends(
    profile_id: int,
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snapshots = trend_for_profile(db, profile_id, limit=limit)
    return [
        {
            "snapshot_at": item.snapshot_at,
            "overall_score": item.overall_score,
            "management_score": item.management_score,
            "technical_score": item.technical_score,
            "evidence_score": item.evidence_score,
            "risk_level": item.risk_level,
        }
        for item in snapshots
    ]
