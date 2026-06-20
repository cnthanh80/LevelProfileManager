from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EnterpriseConfiguration(Base, TimestampMixin):
    __tablename__ = "enterprise_configurations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    config_key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    config_group: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    config_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(40), nullable=False, default="STRING")
    is_secret: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class EnterpriseHealthCheck(Base, TimestampMixin):
    __tablename__ = "enterprise_health_checks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    component_code: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    component_name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_group: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="UNKNOWN", index=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)


class EnterpriseJobSchedule(Base, TimestampMixin):
    __tablename__ = "enterprise_job_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_group: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    schedule_expression: Mapped[str] = mapped_column(String(120), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    last_run_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, index=True)
    next_run_hint: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    last_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class DataRetentionPolicy(Base, TimestampMixin):
    __tablename__ = "data_retention_policies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    policy_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    data_domain: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=365)
    archive_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    purge_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    legal_hold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class BackupRecord(Base, TimestampMixin):
    __tablename__ = "backup_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    backup_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    backup_type: Mapped[str] = mapped_column(String(60), nullable=False, default="LOGICAL", index=True)
    scope: Mapped[str] = mapped_column(String(120), nullable=False, default="DATABASE", index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="COMPLETED", index=True)
    storage_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, index=True)
    validated_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, index=True)
    validation_status: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
