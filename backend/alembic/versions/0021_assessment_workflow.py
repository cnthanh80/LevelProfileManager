"""assessment workflow engine

Revision ID: 0021_assessment_workflow
Revises: 0020_real_signature
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0021_assessment_workflow"
down_revision = "0020_real_signature"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "assessment_workflow_events",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("assessment_cases.id"), nullable=False),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("from_status", sa.String(length=60), nullable=True),
        sa.Column("to_status", sa.String(length=60), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("actor_role", sa.String(length=100), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("assessment_unit", sa.String(length=255), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_assessment_workflow_events_case_id", "assessment_workflow_events", ["case_id"])
    op.create_index("ix_assessment_workflow_events_profile_id", "assessment_workflow_events", ["profile_id"])
    op.create_index("ix_assessment_workflow_events_action", "assessment_workflow_events", ["action"])
    op.create_index("ix_assessment_workflow_events_to_status", "assessment_workflow_events", ["to_status"])


def downgrade():
    op.drop_index("ix_assessment_workflow_events_to_status", table_name="assessment_workflow_events")
    op.drop_index("ix_assessment_workflow_events_action", table_name="assessment_workflow_events")
    op.drop_index("ix_assessment_workflow_events_profile_id", table_name="assessment_workflow_events")
    op.drop_index("ix_assessment_workflow_events_case_id", table_name="assessment_workflow_events")
    op.drop_table("assessment_workflow_events")
