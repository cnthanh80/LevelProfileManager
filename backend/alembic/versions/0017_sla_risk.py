"""sla and risk register

Revision ID: 0017_sla_risk
Revises: 0016_template_center
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0017_sla_risk"
down_revision = "0016_template_center"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_register_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=True),
        sa.Column("information_system_id", sa.Integer(), nullable=True),
        sa.Column("risk_code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=False, server_default="GENERAL"),
        sa.Column("likelihood", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("impact", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("risk_level", sa.String(length=30), nullable=False, server_default="LOW"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="OPEN"),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("mitigation_plan", sa.Text(), nullable=True),
        sa.Column("residual_score", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["level_profiles.id"]),
        sa.ForeignKeyConstraint(["information_system_id"], ["information_systems.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_risk_register_items_risk_code", "risk_register_items", ["risk_code"], unique=True)
    op.create_index("ix_risk_register_items_profile_id", "risk_register_items", ["profile_id"])
    op.create_index("ix_risk_register_items_information_system_id", "risk_register_items", ["information_system_id"])
    op.create_index("ix_risk_register_items_risk_score", "risk_register_items", ["risk_score"])
    op.create_index("ix_risk_register_items_risk_level", "risk_register_items", ["risk_level"])
    op.create_index("ix_risk_register_items_status", "risk_register_items", ["status"])

    op.create_table(
        "sla_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False, server_default="WORKFLOW"),
        sa.Column("workflow_status", sa.String(length=80), nullable=True),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("due_hours", sa.Integer(), nullable=False, server_default="72"),
        sa.Column("warning_hours", sa.Integer(), nullable=False, server_default="24"),
        sa.Column("is_active", sa.String(length=10), nullable=False, server_default="Y"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sla_policies_code", "sla_policies", ["code"], unique=True)
    op.create_index("ix_sla_policies_target_type", "sla_policies", ["target_type"])
    op.create_index("ix_sla_policies_workflow_status", "sla_policies", ["workflow_status"])
    op.create_index("ix_sla_policies_severity", "sla_policies", ["severity"])
    op.create_index("ix_sla_policies_is_active", "sla_policies", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_sla_policies_is_active", table_name="sla_policies")
    op.drop_index("ix_sla_policies_severity", table_name="sla_policies")
    op.drop_index("ix_sla_policies_workflow_status", table_name="sla_policies")
    op.drop_index("ix_sla_policies_target_type", table_name="sla_policies")
    op.drop_index("ix_sla_policies_code", table_name="sla_policies")
    op.drop_table("sla_policies")
    op.drop_index("ix_risk_register_items_status", table_name="risk_register_items")
    op.drop_index("ix_risk_register_items_risk_level", table_name="risk_register_items")
    op.drop_index("ix_risk_register_items_risk_score", table_name="risk_register_items")
    op.drop_index("ix_risk_register_items_information_system_id", table_name="risk_register_items")
    op.drop_index("ix_risk_register_items_profile_id", table_name="risk_register_items")
    op.drop_index("ix_risk_register_items_risk_code", table_name="risk_register_items")
    op.drop_table("risk_register_items")
