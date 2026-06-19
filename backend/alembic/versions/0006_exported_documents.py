"""exported documents

Revision ID: 0006_exported_documents
Revises: 0005_workflow_engine
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_exported_documents"
down_revision = "0005_workflow_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "exported_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("file_format", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("stored_filename", sa.String(length=500), nullable=False),
        sa.Column("storage_path", sa.String(length=1000), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("generated_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["generated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["level_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index(op.f("ix_exported_documents_id"), "exported_documents", ["id"], unique=False)
    op.create_index(op.f("ix_exported_documents_profile_id"), "exported_documents", ["profile_id"], unique=False)
    op.create_index(op.f("ix_exported_documents_document_type"), "exported_documents", ["document_type"], unique=False)
    op.create_index(op.f("ix_exported_documents_file_format"), "exported_documents", ["file_format"], unique=False)
    op.create_index(op.f("ix_exported_documents_checksum_sha256"), "exported_documents", ["checksum_sha256"], unique=False)
    op.create_index(op.f("ix_exported_documents_generated_by"), "exported_documents", ["generated_by"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_exported_documents_generated_by"), table_name="exported_documents")
    op.drop_index(op.f("ix_exported_documents_checksum_sha256"), table_name="exported_documents")
    op.drop_index(op.f("ix_exported_documents_file_format"), table_name="exported_documents")
    op.drop_index(op.f("ix_exported_documents_document_type"), table_name="exported_documents")
    op.drop_index(op.f("ix_exported_documents_profile_id"), table_name="exported_documents")
    op.drop_index(op.f("ix_exported_documents_id"), table_name="exported_documents")
    op.drop_table("exported_documents")
