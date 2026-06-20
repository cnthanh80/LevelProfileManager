from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CmdbAsset(Base, TimestampMixin):
    __tablename__ = "cmdb_assets"
    __table_args__ = (UniqueConstraint("asset_code", name="uq_cmdb_assets_asset_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    asset_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    asset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), default="SERVER", nullable=False, index=True)
    environment: Mapped[str | None] = mapped_column(String(50), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(100))
    hostname: Mapped[str | None] = mapped_column(String(255))
    operating_system: Mapped[str | None] = mapped_column(String(255))
    owner_org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"))
    information_system_id: Mapped[int | None] = mapped_column(ForeignKey("information_systems.id"), index=True)
    criticality: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)


class CmdbApplication(Base, TimestampMixin):
    __tablename__ = "cmdb_applications"
    __table_args__ = (UniqueConstraint("app_code", name="uq_cmdb_applications_app_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    app_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    app_name: Mapped[str] = mapped_column(String(255), nullable=False)
    information_system_id: Mapped[int | None] = mapped_column(ForeignKey("information_systems.id"), index=True)
    owner_org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"))
    app_type: Mapped[str] = mapped_column(String(80), default="BUSINESS", nullable=False)
    technology_stack: Mapped[str | None] = mapped_column(Text)
    internet_exposed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_api: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class CmdbDatabase(Base, TimestampMixin):
    __tablename__ = "cmdb_databases"
    __table_args__ = (UniqueConstraint("db_code", name="uq_cmdb_databases_db_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    db_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    db_name: Mapped[str] = mapped_column(String(255), nullable=False)
    information_system_id: Mapped[int | None] = mapped_column(ForeignKey("information_systems.id"), index=True)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("cmdb_assets.id"))
    db_type: Mapped[str] = mapped_column(String(80), default="ORACLE", nullable=False)
    data_classification: Mapped[str] = mapped_column(String(80), default="INTERNAL", nullable=False)
    contains_personal_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contains_financial_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    size_gb: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class CmdbNetworkDevice(Base, TimestampMixin):
    __tablename__ = "cmdb_network_devices"
    __table_args__ = (UniqueConstraint("device_code", name="uq_cmdb_network_devices_device_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    device_name: Mapped[str] = mapped_column(String(255), nullable=False)
    information_system_id: Mapped[int | None] = mapped_column(ForeignKey("information_systems.id"), index=True)
    device_type: Mapped[str] = mapped_column(String(80), default="SWITCH", nullable=False)
    zone: Mapped[str | None] = mapped_column(String(100))
    ip_address: Mapped[str | None] = mapped_column(String(100))
    ha_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    internet_edge: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class CmdbRelationship(Base, TimestampMixin):
    __tablename__ = "cmdb_relationships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(80), default="DEPENDS_ON", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
