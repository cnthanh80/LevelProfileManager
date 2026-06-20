from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EnterpriseReportSnapshot(Base, TimestampMixin):
    __tablename__ = "enterprise_report_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    snapshot_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(30), nullable=False, default="MONTHLY", index=True)
    period_label: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    total_systems: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_profiles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level_1_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level_2_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level_3_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level_4_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level_5_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overall_compliance_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    high_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    overdue_review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_findings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assessment_cases_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    generated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class DataWarehouseMetric(Base, TimestampMixin):
    __tablename__ = "data_warehouse_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    metric_code: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    metric_group: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dimension_key: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    dimension_value: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    measured_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)


class ReportExportJob(Base, TimestampMixin):
    __tablename__ = "report_export_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    export_format: Mapped[str] = mapped_column(String(20), nullable=False, default="CSV", index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="COMPLETED", index=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    requested_by: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    generated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
