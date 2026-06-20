"""siem and audit integration

Revision ID: 0023_siem_integration
Revises: 0022_cmdb_assets
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0023_siem_integration"
down_revision = "0022_cmdb_assets"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "siem_connectors",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("connector_code", sa.String(length=100), nullable=False),
        sa.Column("connector_name", sa.String(length=255), nullable=False),
        sa.Column("connector_type", sa.String(length=80), nullable=False, server_default="SYSLOG"),
        sa.Column("endpoint_url", sa.String(length=500), nullable=True),
        sa.Column("auth_type", sa.String(length=80), nullable=True, server_default="NONE"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("connector_code", name="uq_siem_connectors_code"),
    )
    op.create_index("ix_siem_connectors_connector_code", "siem_connectors", ["connector_code"])
    op.create_index("ix_siem_connectors_connector_type", "siem_connectors", ["connector_type"])
    op.create_index("ix_siem_connectors_is_enabled", "siem_connectors", ["is_enabled"])

    op.create_table(
        "siem_events",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("connector_id", sa.Integer(), sa.ForeignKey("siem_connectors.id"), nullable=True),
        sa.Column("source_system", sa.String(length=150), nullable=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default="INFO"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="OPEN"),
        sa.Column("username", sa.String(length=150), nullable=True),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column("asset_code", sa.String(length=100), nullable=True),
        sa.Column("information_system_id", sa.Integer(), sa.ForeignKey("information_systems.id"), nullable=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=True),
        sa.Column("correlation_key", sa.String(length=200), nullable=True),
        sa.Column("raw_message", sa.Text(), nullable=True),
        sa.Column("normalized_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_siem_events_connector_id", "siem_events", ["connector_id"])
    op.create_index("ix_siem_events_event_type", "siem_events", ["event_type"])
    op.create_index("ix_siem_events_severity", "siem_events", ["severity"])
    op.create_index("ix_siem_events_status", "siem_events", ["status"])
    op.create_index("ix_siem_events_profile_id", "siem_events", ["profile_id"])
    op.create_index("ix_siem_events_information_system_id", "siem_events", ["information_system_id"])
    op.create_index("ix_siem_events_correlation_key", "siem_events", ["correlation_key"])
    op.create_index("ix_siem_events_ip_address", "siem_events", ["ip_address"])

    op.create_table(
        "siem_correlation_rules",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("rule_code", sa.String(length=100), nullable=False),
        sa.Column("rule_name", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=True),
        sa.Column("min_severity", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("threshold_count", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("window_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("action_hint", sa.Text(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("rule_code", name="uq_siem_rules_code"),
    )
    op.create_index("ix_siem_rules_rule_code", "siem_correlation_rules", ["rule_code"])
    op.create_index("ix_siem_rules_event_type", "siem_correlation_rules", ["event_type"])
    op.create_index("ix_siem_rules_is_enabled", "siem_correlation_rules", ["is_enabled"])


def downgrade():
    op.drop_index("ix_siem_rules_is_enabled", table_name="siem_correlation_rules")
    op.drop_index("ix_siem_rules_event_type", table_name="siem_correlation_rules")
    op.drop_index("ix_siem_rules_rule_code", table_name="siem_correlation_rules")
    op.drop_table("siem_correlation_rules")
    op.drop_index("ix_siem_events_ip_address", table_name="siem_events")
    op.drop_index("ix_siem_events_correlation_key", table_name="siem_events")
    op.drop_index("ix_siem_events_information_system_id", table_name="siem_events")
    op.drop_index("ix_siem_events_profile_id", table_name="siem_events")
    op.drop_index("ix_siem_events_status", table_name="siem_events")
    op.drop_index("ix_siem_events_severity", table_name="siem_events")
    op.drop_index("ix_siem_events_event_type", table_name="siem_events")
    op.drop_index("ix_siem_events_connector_id", table_name="siem_events")
    op.drop_table("siem_events")
    op.drop_index("ix_siem_connectors_is_enabled", table_name="siem_connectors")
    op.drop_index("ix_siem_connectors_connector_type", table_name="siem_connectors")
    op.drop_index("ix_siem_connectors_connector_code", table_name="siem_connectors")
    op.drop_table("siem_connectors")
