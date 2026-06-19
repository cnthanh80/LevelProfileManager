"""periodic review engine

Revision ID: 0009_periodic_review_engine
Revises: 0008_compliance_engine
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_periodic_review_engine"
down_revision = "0008_compliance_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "periodic_reviews",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False, index=True),
        sa.Column("review_code", sa.String(length=120), nullable=False, unique=True, index=True),
        sa.Column("review_type", sa.String(length=50), nullable=False, server_default="ANNUAL", index=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PLANNED", index=True),
        sa.Column("due_date", sa.Date(), nullable=False, index=True),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("completed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("action_plan", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("periodic_reviews")
