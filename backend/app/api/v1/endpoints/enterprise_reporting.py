from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enterprise_reporting import DataWarehouseMetric, EnterpriseReportSnapshot
from app.models.user import User
from app.schemas.common import Page
from app.schemas.enterprise_reporting import (
    DataWarehouseMetricRead,
    EnterpriseReportingDashboard,
    EnterpriseReportingGenerateRequest,
    EnterpriseReportingSummary,
    EnterpriseReportSnapshotRead,
)
from app.services.enterprise_reporting_service import (
    calculate_enterprise_summary,
    generate_enterprise_snapshot,
    portfolio_csv,
    reporting_dashboard,
)

router = APIRouter()


@router.get("/dashboard/enterprise-reporting", response_model=EnterpriseReportingDashboard)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return reporting_dashboard(db)


@router.get("/enterprise-reporting/summary", response_model=EnterpriseReportingSummary)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return calculate_enterprise_summary(db)


@router.post("/enterprise-reporting/snapshots/generate", response_model=EnterpriseReportSnapshotRead)
def generate_snapshot(
    payload: EnterpriseReportingGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "SECURITY_OFFICER", "REVIEWER")),
):
    return generate_enterprise_snapshot(db, period_type=payload.period_type, period_label=payload.period_label, refresh_metrics=payload.refresh_metrics)


@router.get("/enterprise-reporting/snapshots", response_model=Page[EnterpriseReportSnapshotRead])
def snapshots(
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.scalar(select(func.count(EnterpriseReportSnapshot.id))) or 0
    items = db.scalars(select(EnterpriseReportSnapshot).order_by(EnterpriseReportSnapshot.generated_at.desc()).limit(limit).offset(offset)).all()
    return Page[EnterpriseReportSnapshotRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/enterprise-reporting/data-warehouse/metrics", response_model=Page[DataWarehouseMetricRead])
def metrics(
    metric_group: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(DataWarehouseMetric)
    count_stmt = select(func.count(DataWarehouseMetric.id))
    if metric_group:
        stmt = stmt.where(DataWarehouseMetric.metric_group == metric_group.upper())
        count_stmt = count_stmt.where(DataWarehouseMetric.metric_group == metric_group.upper())
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(DataWarehouseMetric.measured_at.desc(), DataWarehouseMetric.id.desc()).limit(limit).offset(offset)).all()
    return Page[DataWarehouseMetricRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/enterprise-reporting/export/portfolio-csv")
def export_portfolio_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    text = portfolio_csv(db, requested_by=current_user.id)
    return PlainTextResponse(text, media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=portfolio-summary.csv"})
