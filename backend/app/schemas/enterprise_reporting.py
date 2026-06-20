from datetime import datetime
from pydantic import BaseModel


class EnterpriseReportSnapshotRead(BaseModel):
    id: int
    snapshot_code: str
    period_type: str
    period_label: str
    total_systems: int
    total_profiles: int
    level_1_count: int
    level_2_count: int
    level_3_count: int
    level_4_count: int
    level_5_count: int
    overall_compliance_score: int
    high_risk_count: int
    overdue_review_count: int
    open_findings_count: int
    assessment_cases_count: int
    generated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DataWarehouseMetricRead(BaseModel):
    id: int
    metric_code: str
    metric_group: str
    metric_name: str
    metric_value: int
    dimension_key: str | None = None
    dimension_value: str | None = None
    measured_at: datetime

    model_config = {"from_attributes": True}


class ReportExportJobRead(BaseModel):
    id: int
    job_code: str
    report_type: str
    export_format: str
    status: str
    file_path: str | None = None
    requested_by: int | None = None
    generated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class EnterpriseReportingGenerateRequest(BaseModel):
    period_type: str = "MONTHLY"
    period_label: str | None = None
    refresh_metrics: bool = True


class EnterpriseReportingSummary(BaseModel):
    total_systems: int
    total_profiles: int
    level_distribution: dict[str, int]
    portfolio_average_score: int
    high_risk_count: int
    overdue_review_count: int
    open_findings_count: int
    assessment_cases_count: int
    latest_snapshot: EnterpriseReportSnapshotRead | None = None
    recommendations: list[str]


class EnterpriseReportingDashboard(BaseModel):
    summary: EnterpriseReportingSummary
    recent_snapshots: list[EnterpriseReportSnapshotRead]
    data_warehouse_metrics: list[DataWarehouseMetricRead]
    board_pack: dict
