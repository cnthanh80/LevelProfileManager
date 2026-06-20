"""cmdb and asset inventory

Revision ID: 0022_cmdb_assets
Revises: 0021_assessment_workflow
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0022_cmdb_assets"
down_revision = "0021_assessment_workflow"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cmdb_assets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("asset_code", sa.String(length=100), nullable=False),
        sa.Column("asset_name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False, server_default="SERVER"),
        sa.Column("environment", sa.String(length=50), nullable=True),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("operating_system", sa.String(length=255), nullable=True),
        sa.Column("owner_org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("information_system_id", sa.Integer(), sa.ForeignKey("information_systems.id"), nullable=True),
        sa.Column("criticality", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("asset_code", name="uq_cmdb_assets_asset_code"),
    )
    op.create_index("ix_cmdb_assets_asset_code", "cmdb_assets", ["asset_code"])
    op.create_index("ix_cmdb_assets_asset_type", "cmdb_assets", ["asset_type"])
    op.create_index("ix_cmdb_assets_information_system_id", "cmdb_assets", ["information_system_id"])
    op.create_index("ix_cmdb_assets_status", "cmdb_assets", ["status"])

    op.create_table(
        "cmdb_applications",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("app_code", sa.String(length=100), nullable=False),
        sa.Column("app_name", sa.String(length=255), nullable=False),
        sa.Column("information_system_id", sa.Integer(), sa.ForeignKey("information_systems.id"), nullable=True),
        sa.Column("owner_org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("app_type", sa.String(length=80), nullable=False, server_default="BUSINESS"),
        sa.Column("technology_stack", sa.Text(), nullable=True),
        sa.Column("internet_exposed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("has_api", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("app_code", name="uq_cmdb_applications_app_code"),
    )
    op.create_index("ix_cmdb_applications_app_code", "cmdb_applications", ["app_code"])
    op.create_index("ix_cmdb_applications_information_system_id", "cmdb_applications", ["information_system_id"])

    op.create_table(
        "cmdb_databases",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("db_code", sa.String(length=100), nullable=False),
        sa.Column("db_name", sa.String(length=255), nullable=False),
        sa.Column("information_system_id", sa.Integer(), sa.ForeignKey("information_systems.id"), nullable=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("cmdb_assets.id"), nullable=True),
        sa.Column("db_type", sa.String(length=80), nullable=False, server_default="ORACLE"),
        sa.Column("data_classification", sa.String(length=80), nullable=False, server_default="INTERNAL"),
        sa.Column("contains_personal_data", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("contains_financial_data", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("size_gb", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("db_code", name="uq_cmdb_databases_db_code"),
    )
    op.create_index("ix_cmdb_databases_db_code", "cmdb_databases", ["db_code"])
    op.create_index("ix_cmdb_databases_information_system_id", "cmdb_databases", ["information_system_id"])

    op.create_table(
        "cmdb_network_devices",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("device_code", sa.String(length=100), nullable=False),
        sa.Column("device_name", sa.String(length=255), nullable=False),
        sa.Column("information_system_id", sa.Integer(), sa.ForeignKey("information_systems.id"), nullable=True),
        sa.Column("device_type", sa.String(length=80), nullable=False, server_default="SWITCH"),
        sa.Column("zone", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column("ha_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("internet_edge", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("device_code", name="uq_cmdb_network_devices_device_code"),
    )
    op.create_index("ix_cmdb_network_devices_device_code", "cmdb_network_devices", ["device_code"])
    op.create_index("ix_cmdb_network_devices_information_system_id", "cmdb_network_devices", ["information_system_id"])

    op.create_table(
        "cmdb_relationships",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("relationship_type", sa.String(length=80), nullable=False, server_default="DEPENDS_ON"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_cmdb_relationships_source", "cmdb_relationships", ["source_type", "source_id"])
    op.create_index("ix_cmdb_relationships_target", "cmdb_relationships", ["target_type", "target_id"])


def downgrade():
    op.drop_index("ix_cmdb_relationships_target", table_name="cmdb_relationships")
    op.drop_index("ix_cmdb_relationships_source", table_name="cmdb_relationships")
    op.drop_table("cmdb_relationships")
    op.drop_index("ix_cmdb_network_devices_information_system_id", table_name="cmdb_network_devices")
    op.drop_index("ix_cmdb_network_devices_device_code", table_name="cmdb_network_devices")
    op.drop_table("cmdb_network_devices")
    op.drop_index("ix_cmdb_databases_information_system_id", table_name="cmdb_databases")
    op.drop_index("ix_cmdb_databases_db_code", table_name="cmdb_databases")
    op.drop_table("cmdb_databases")
    op.drop_index("ix_cmdb_applications_information_system_id", table_name="cmdb_applications")
    op.drop_index("ix_cmdb_applications_app_code", table_name="cmdb_applications")
    op.drop_table("cmdb_applications")
    op.drop_index("ix_cmdb_assets_status", table_name="cmdb_assets")
    op.drop_index("ix_cmdb_assets_information_system_id", table_name="cmdb_assets")
    op.drop_index("ix_cmdb_assets_asset_type", table_name="cmdb_assets")
    op.drop_index("ix_cmdb_assets_asset_code", table_name="cmdb_assets")
    op.drop_table("cmdb_assets")
