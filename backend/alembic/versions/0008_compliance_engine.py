"""compliance engine

Revision ID: 0008_compliance_engine
Revises: 0007_notification_audit
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_compliance_engine"
down_revision = "0007_notification_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profile_assessments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False, index=True),
        sa.Column("suggested_level", sa.Integer(), nullable=False, index=True),
        sa.Column("current_level", sa.Integer(), nullable=False, index=True),
        sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="70"),
        sa.Column("classification_reasons", sa.Text(), nullable=True),
        sa.Column("missing_requirements", sa.Text(), nullable=True),
        sa.Column("readiness_status", sa.String(length=50), nullable=False, server_default="NOT_READY"),
        sa.Column("readiness_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_ready_for_assessment", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("assessed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "compliance_scores",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False, index=True),
        sa.Column("management_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("technical_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mandatory_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mandatory_compliant", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gap_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score_status", sa.String(length=50), nullable=False, server_default="CALCULATED"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False, index=True),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(length=30), nullable=False, server_default="LOW", index=True),
        sa.Column("risk_factors", sa.Text(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("risk_assessments")
    op.drop_table("compliance_scores")
    op.drop_table("profile_assessments")
