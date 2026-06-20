from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ComplianceSnapshot(Base, TimestampMixin):
    __tablename__ = "compliance_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    snapshot_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    profile_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    system_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organization_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    proposed_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    management_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    technical_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    automation_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    risk_level: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM", index=True)
    trend_direction: Mapped[str] = mapped_column(String(30), nullable=False, default="STABLE", index=True)
    gap_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mandatory_gap_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing_evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_finding_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    snapshot_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class ComplianceMonitoringFinding(Base, TimestampMixin):
    __tablename__ = "compliance_monitoring_findings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    snapshot_id: Mapped[int | None] = mapped_column(ForeignKey("compliance_snapshots.id"), nullable=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("level_profiles.id"), nullable=False, index=True)
    finding_code: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    finding_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM", index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="OPEN", index=True)


class ComplianceMonitoringNotification(Base, TimestampMixin):
    __tablename__ = "compliance_monitoring_notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    snapshot_id: Mapped[int | None] = mapped_column(ForeignKey("compliance_snapshots.id"), nullable=True, index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("level_profiles.id"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False, default="IN_APP", index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    recipient: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="DRY_RUN", index=True)
