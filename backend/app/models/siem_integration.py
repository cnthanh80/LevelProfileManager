from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SiemConnector(Base, TimestampMixin):
    __tablename__ = "siem_connectors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    connector_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    connector_name: Mapped[str] = mapped_column(String(255), nullable=False)
    connector_type: Mapped[str] = mapped_column(String(80), nullable=False, default="SYSLOG", index=True)
    endpoint_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    auth_type: Mapped[str | None] = mapped_column(String(80), nullable=True, default="NONE")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    last_sync_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class SiemEvent(Base, TimestampMixin):
    __tablename__ = "siem_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    connector_id: Mapped[int | None] = mapped_column(ForeignKey("siem_connectors.id"), nullable=True, index=True)
    source_system: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="INFO", index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN", index=True)
    username: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    asset_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    information_system_id: Mapped[int | None] = mapped_column(ForeignKey("information_systems.id"), nullable=True, index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("level_profiles.id"), nullable=True, index=True)
    correlation_key: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    raw_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class SiemCorrelationRule(Base, TimestampMixin):
    __tablename__ = "siem_correlation_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    min_severity: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM")
    threshold_count: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    window_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    action_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
