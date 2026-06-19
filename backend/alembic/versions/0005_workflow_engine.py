"""workflow engine approval comments

Revision ID: 0005_workflow_engine
Revises: 0004_evidence_documents
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_workflow_engine"
down_revision: Union[str, None] = "0004_evidence_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "approval_comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("workflow_state", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_approval_comments_id", "approval_comments", ["id"])
    op.create_index("ix_approval_comments_profile_id", "approval_comments", ["profile_id"])
    op.create_index("ix_approval_comments_workflow_state", "approval_comments", ["workflow_state"])
    op.create_index("ix_approval_comments_action", "approval_comments", ["action"])
    op.create_index("ix_approval_comments_created_by", "approval_comments", ["created_by"])


def downgrade() -> None:
    op.drop_table("approval_comments")
