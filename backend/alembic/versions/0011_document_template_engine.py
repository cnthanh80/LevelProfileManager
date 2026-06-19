"""document template engine

Revision ID: 0011_document_template_engine
Revises: 0010_audit_trail_enhancement
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_document_template_engine"
down_revision = "0010_audit_trail_enhancement"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False, server_default="1.0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("agency_name", sa.String(length=255), nullable=True),
        sa.Column("file_format", sa.String(length=20), nullable=False, server_default="docx"),
        sa.Column("template_path", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_templates_id"), "document_templates", ["id"], unique=False)
    op.create_index(op.f("ix_document_templates_code"), "document_templates", ["code"], unique=True)
    op.create_index(op.f("ix_document_templates_document_type"), "document_templates", ["document_type"], unique=False)
    op.create_index(op.f("ix_document_templates_is_active"), "document_templates", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_document_templates_is_active"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_document_type"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_code"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_id"), table_name="document_templates")
    op.drop_table("document_templates")
