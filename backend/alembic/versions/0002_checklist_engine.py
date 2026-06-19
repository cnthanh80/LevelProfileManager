"""checklist engine

Revision ID: 0002_checklist_engine
Revises: 0001_initial_core_schema
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_checklist_engine"
down_revision: Union[str, None] = "0001_initial_core_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "security_requirements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("group_name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("required_level", sa.Integer(), nullable=False),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_security_requirements_id", "security_requirements", ["id"])
    op.create_index("ix_security_requirements_code", "security_requirements", ["code"])
    op.create_index("ix_security_requirements_group_name", "security_requirements", ["group_name"])
    op.create_index("ix_security_requirements_category", "security_requirements", ["category"])
    op.create_index("ix_security_requirements_required_level", "security_requirements", ["required_level"])

    op.create_table(
        "profile_requirement_answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("requirement_id", sa.Integer(), sa.ForeignKey("security_requirements.id"), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="NON_COMPLIANT"),
        sa.Column("current_state", sa.Text(), nullable=True),
        sa.Column("improvement_plan", sa.Text(), nullable=True),
        sa.Column("evidence_note", sa.Text(), nullable=True),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("profile_id", "requirement_id", name="uq_profile_requirement_answer"),
    )
    op.create_index("ix_profile_requirement_answers_id", "profile_requirement_answers", ["id"])
    op.create_index("ix_profile_requirement_answers_profile_id", "profile_requirement_answers", ["profile_id"])
    op.create_index("ix_profile_requirement_answers_requirement_id", "profile_requirement_answers", ["requirement_id"])
    op.create_index("ix_profile_requirement_answers_status", "profile_requirement_answers", ["status"])


def downgrade() -> None:
    op.drop_table("profile_requirement_answers")
    op.drop_table("security_requirements")
