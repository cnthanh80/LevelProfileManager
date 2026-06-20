from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class RiskRegisterItem(Base, TimestampMixin):
    __tablename__ = "risk_register_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("level_profiles.id"), nullable=True, index=True)
    information_system_id: Mapped[int | None] = mapped_column(ForeignKey("information_systems.id"), nullable=True, index=True)
    risk_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), default="GENERAL", nullable=False, index=True)
    likelihood: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=1, nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(30), default="LOW", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), default="OPEN", nullable=False, index=True)
    owner: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[date | None] = mapped_column(Date)
    mitigation_plan: Mapped[str | None] = mapped_column(Text)
    residual_score: Mapped[int | None] = mapped_column(Integer)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class SlaPolicy(Base, TimestampMixin):
    __tablename__ = "sla_policies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(80), default="WORKFLOW", nullable=False, index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(80), index=True)
    severity: Mapped[str] = mapped_column(String(30), default="MEDIUM", nullable=False, index=True)
    due_hours: Mapped[int] = mapped_column(Integer, default=72, nullable=False)
    warning_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    is_active: Mapped[str] = mapped_column(String(10), default="Y", nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
