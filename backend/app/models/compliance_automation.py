from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ComplianceAutomationRule(Base, TimestampMixin):
    __tablename__ = "compliance_automation_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM", index=True)
    threshold_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation_template: Mapped[str | None] = mapped_column(Text, nullable=True)


class ComplianceAutomationRun(Base, TimestampMixin):
    __tablename__ = "compliance_automation_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(80), nullable=False, default="ALL_PROFILES", index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("level_profiles.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="COMPLETED", index=True)
    total_profiles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_findings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_findings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_findings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    readiness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class ComplianceAutomationFinding(Base, TimestampMixin):
    __tablename__ = "compliance_automation_findings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("compliance_automation_runs.id"), nullable=False, index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("level_profiles.id"), nullable=True, index=True)
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    finding_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM", index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="OPEN", index=True)
