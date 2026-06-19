"""evidence documents

Revision ID: 0004_evidence_documents
Revises: 0003_fix_seed_user_emails
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_evidence_documents"
down_revision: Union[str, None] = "0003_fix_seed_user_emails"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evidence_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("checklist_answer_id", sa.Integer(), sa.ForeignKey("profile_requirement_answers.id"), nullable=True),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("stored_filename", sa.String(length=500), nullable=False, unique=True),
        sa.Column("storage_path", sa.String(length=1000), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_evidence_documents_id", "evidence_documents", ["id"])
    op.create_index("ix_evidence_documents_profile_id", "evidence_documents", ["profile_id"])
    op.create_index("ix_evidence_documents_checklist_answer_id", "evidence_documents", ["checklist_answer_id"])
    op.create_index("ix_evidence_documents_document_type", "evidence_documents", ["document_type"])
    op.create_index("ix_evidence_documents_checksum_sha256", "evidence_documents", ["checksum_sha256"])
    op.create_index("ix_evidence_documents_uploaded_by", "evidence_documents", ["uploaded_by"])


def downgrade() -> None:
    op.drop_table("evidence_documents")
