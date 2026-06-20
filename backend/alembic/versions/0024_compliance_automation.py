"""compliance automation

Revision ID: 0024_compliance_auto
Revises: 0023_siem_integration
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0024_compliance_auto"
down_revision = "0023_siem_integration"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "compliance_automation_rules",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("rule_code", sa.String(length=100), nullable=False),
        sa.Column("rule_name", sa.String(length=255), nullable=False),
        sa.Column("rule_type", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("threshold_value", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("recommendation_template", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("rule_code", name="uq_compliance_auto_rules_code"),
    )
    op.create_index("ix_compliance_auto_rules_code", "compliance_automation_rules", ["rule_code"])
    op.create_index("ix_compliance_auto_rules_type", "compliance_automation_rules", ["rule_type"])
    op.create_index("ix_compliance_auto_rules_enabled", "compliance_automation_rules", ["is_enabled"])

    op.create_table(
        "compliance_automation_runs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("run_code", sa.String(length=120), nullable=False),
        sa.Column("scope", sa.String(length=80), nullable=False, server_default="ALL_PROFILES"),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="COMPLETED"),
        sa.Column("total_profiles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_findings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("high_findings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("critical_findings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("readiness_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("executive_summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("run_code", name="uq_compliance_auto_runs_code"),
    )
    op.create_index("ix_compliance_auto_runs_code", "compliance_automation_runs", ["run_code"])
    op.create_index("ix_compliance_auto_runs_profile", "compliance_automation_runs", ["profile_id"])
    op.create_index("ix_compliance_auto_runs_status", "compliance_automation_runs", ["status"])

    op.create_table(
        "compliance_automation_findings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("compliance_automation_runs.id"), nullable=False),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=True),
        sa.Column("rule_code", sa.String(length=100), nullable=False),
        sa.Column("finding_type", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_compliance_auto_findings_run", "compliance_automation_findings", ["run_id"])
    op.create_index("ix_compliance_auto_findings_profile", "compliance_automation_findings", ["profile_id"])
    op.create_index("ix_compliance_auto_findings_type", "compliance_automation_findings", ["finding_type"])
    op.create_index("ix_compliance_auto_findings_severity", "compliance_automation_findings", ["severity"])
    op.create_index("ix_compliance_auto_findings_status", "compliance_automation_findings", ["status"])


def downgrade():
    op.drop_index("ix_compliance_auto_findings_status", table_name="compliance_automation_findings")
    op.drop_index("ix_compliance_auto_findings_severity", table_name="compliance_automation_findings")
    op.drop_index("ix_compliance_auto_findings_type", table_name="compliance_automation_findings")
    op.drop_index("ix_compliance_auto_findings_profile", table_name="compliance_automation_findings")
    op.drop_index("ix_compliance_auto_findings_run", table_name="compliance_automation_findings")
    op.drop_table("compliance_automation_findings")
    op.drop_index("ix_compliance_auto_runs_status", table_name="compliance_automation_runs")
    op.drop_index("ix_compliance_auto_runs_profile", table_name="compliance_automation_runs")
    op.drop_index("ix_compliance_auto_runs_code", table_name="compliance_automation_runs")
    op.drop_table("compliance_automation_runs")
    op.drop_index("ix_compliance_auto_rules_enabled", table_name="compliance_automation_rules")
    op.drop_index("ix_compliance_auto_rules_type", table_name="compliance_automation_rules")
    op.drop_index("ix_compliance_auto_rules_code", table_name="compliance_automation_rules")
    op.drop_table("compliance_automation_rules")
