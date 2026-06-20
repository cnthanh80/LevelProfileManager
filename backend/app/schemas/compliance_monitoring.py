from datetime import datetime
from pydantic import BaseModel, Field


class ComplianceMonitoringRunRequest(BaseModel):
    profile_id: int | None = None
    scope: str = "ALL_PROFILES"
    create_notifications: bool = True


class ComplianceSnapshotRead(BaseModel):
    id: int
    snapshot_code: str
    profile_id: int
    profile_code: str
    system_name: str | None = None
    organization_name: str | None = None
    proposed_level: int
    management_score: int
    technical_score: int
    evidence_score: int
    automation_score: int
    overall_score: int
    risk_level: str
    trend_direction: str
    gap_count: int
    mandatory_gap_count: int
    missing_evidence_count: int
    open_finding_count: int
    snapshot_at: datetime
    summary: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplianceMonitoringFindingRead(BaseModel):
    id: int
    snapshot_id: int | None = None
    profile_id: int
    finding_code: str
    finding_type: str
    severity: str
    title: str
    description: str | None = None
    recommendation: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplianceMonitoringNotificationRead(BaseModel):
    id: int
    snapshot_id: int | None = None
    profile_id: int | None = None
    channel: str
    event_type: str
    recipient: str | None = None
    subject: str
    message: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplianceMonitoringRunResult(BaseModel):
    status: str
    scope: str
    total_profiles: int
    snapshots_created: int
    findings_created: int
    notifications_created: int
    average_score: int
    recommendations: list[str]


class ComplianceMonitoringScoreResult(BaseModel):
    profile_id: int
    profile_code: str
    proposed_level: int
    management_score: int = Field(ge=0, le=100)
    technical_score: int = Field(ge=0, le=100)
    evidence_score: int = Field(ge=0, le=100)
    automation_score: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)
    risk_level: str
    trend_direction: str
    gap_count: int
    mandatory_gap_count: int
    missing_evidence_count: int
    open_finding_count: int
    recommendations: list[str]


class ComplianceHeatmapItem(BaseModel):
    profile_id: int
    profile_code: str
    system_name: str | None = None
    organization_name: str | None = None
    proposed_level: int
    overall_score: int
    risk_level: str
    heat_color: str
    mandatory_gap_count: int
    missing_evidence_count: int
    open_finding_count: int


class ComplianceTrendPoint(BaseModel):
    snapshot_at: datetime
    overall_score: int
    management_score: int
    technical_score: int
    evidence_score: int
    risk_level: str


class ComplianceMonitoringDashboard(BaseModel):
    latest_snapshots: list[ComplianceSnapshotRead]
    portfolio_average_score: int
    total_profiles_monitored: int
    high_risk_profiles: int
    open_findings: int
    notifications: int
    top_risk_profiles: list[ComplianceHeatmapItem]
    recommendations: list[str]
