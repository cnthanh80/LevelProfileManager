"""continuous compliance monitoring

Revision ID: 0025_compliance_mon
Revises: 0024_compliance_auto
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0025_compliance_mon"
down_revision = "0024_compliance_auto"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "compliance_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("snapshot_code", sa.String(length=120), nullable=False),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("profile_code", sa.String(length=100), nullable=False),
        sa.Column("system_name", sa.String(length=255), nullable=True),
        sa.Column("organization_name", sa.String(length=255), nullable=True),
        sa.Column("proposed_level", sa.Integer(), nullable=False),
        sa.Column("management_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("technical_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("evidence_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("automation_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("trend_direction", sa.String(length=30), nullable=False, server_default="STABLE"),
        sa.Column("gap_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mandatory_gap_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missing_evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_finding_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("snapshot_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("snapshot_code", name="uq_compliance_snapshots_code"),
    )
    op.create_index("ix_compliance_snapshots_code", "compliance_snapshots", ["snapshot_code"])
    op.create_index("ix_compliance_snapshots_profile", "compliance_snapshots", ["profile_id"])
    op.create_index("ix_compliance_snapshots_profile_code", "compliance_snapshots", ["profile_code"])
    op.create_index("ix_compliance_snapshots_level", "compliance_snapshots", ["proposed_level"])
    op.create_index("ix_compliance_snapshots_score", "compliance_snapshots", ["overall_score"])
    op.create_index("ix_compliance_snapshots_risk", "compliance_snapshots", ["risk_level"])
    op.create_index("ix_compliance_snapshots_trend", "compliance_snapshots", ["trend_direction"])
    op.create_index("ix_compliance_snapshots_at", "compliance_snapshots", ["snapshot_at"])

    op.create_table(
        "compliance_monitoring_findings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("snapshot_id", sa.Integer(), sa.ForeignKey("compliance_snapshots.id"), nullable=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("finding_code", sa.String(length=120), nullable=False),
        sa.Column("finding_type", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cm_findings_snapshot", "compliance_monitoring_findings", ["snapshot_id"])
    op.create_index("ix_cm_findings_profile", "compliance_monitoring_findings", ["profile_id"])
    op.create_index("ix_cm_findings_code", "compliance_monitoring_findings", ["finding_code"])
    op.create_index("ix_cm_findings_type", "compliance_monitoring_findings", ["finding_type"])
    op.create_index("ix_cm_findings_severity", "compliance_monitoring_findings", ["severity"])
    op.create_index("ix_cm_findings_status", "compliance_monitoring_findings", ["status"])

    op.create_table(
        "compliance_monitoring_notifications",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("snapshot_id", sa.Integer(), sa.ForeignKey("compliance_snapshots.id"), nullable=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=True),
        sa.Column("channel", sa.String(length=40), nullable=False, server_default="IN_APP"),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="DRY_RUN"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_cm_notifications_snapshot", "compliance_monitoring_notifications", ["snapshot_id"])
    op.create_index("ix_cm_notifications_profile", "compliance_monitoring_notifications", ["profile_id"])
    op.create_index("ix_cm_notifications_channel", "compliance_monitoring_notifications", ["channel"])
    op.create_index("ix_cm_notifications_event", "compliance_monitoring_notifications", ["event_type"])
    op.create_index("ix_cm_notifications_status", "compliance_monitoring_notifications", ["status"])


def downgrade():
    op.drop_index("ix_cm_notifications_status", table_name="compliance_monitoring_notifications")
    op.drop_index("ix_cm_notifications_event", table_name="compliance_monitoring_notifications")
    op.drop_index("ix_cm_notifications_channel", table_name="compliance_monitoring_notifications")
    op.drop_index("ix_cm_notifications_profile", table_name="compliance_monitoring_notifications")
    op.drop_index("ix_cm_notifications_snapshot", table_name="compliance_monitoring_notifications")
    op.drop_table("compliance_monitoring_notifications")
    op.drop_index("ix_cm_findings_status", table_name="compliance_monitoring_findings")
    op.drop_index("ix_cm_findings_severity", table_name="compliance_monitoring_findings")
    op.drop_index("ix_cm_findings_type", table_name="compliance_monitoring_findings")
    op.drop_index("ix_cm_findings_code", table_name="compliance_monitoring_findings")
    op.drop_index("ix_cm_findings_profile", table_name="compliance_monitoring_findings")
    op.drop_index("ix_cm_findings_snapshot", table_name="compliance_monitoring_findings")
    op.drop_table("compliance_monitoring_findings")
    op.drop_index("ix_compliance_snapshots_at", table_name="compliance_snapshots")
    op.drop_index("ix_compliance_snapshots_trend", table_name="compliance_snapshots")
    op.drop_index("ix_compliance_snapshots_risk", table_name="compliance_snapshots")
    op.drop_index("ix_compliance_snapshots_score", table_name="compliance_snapshots")
    op.drop_index("ix_compliance_snapshots_level", table_name="compliance_snapshots")
    op.drop_index("ix_compliance_snapshots_profile_code", table_name="compliance_snapshots")
    op.drop_index("ix_compliance_snapshots_profile", table_name="compliance_snapshots")
    op.drop_index("ix_compliance_snapshots_code", table_name="compliance_snapshots")
    op.drop_table("compliance_snapshots")
