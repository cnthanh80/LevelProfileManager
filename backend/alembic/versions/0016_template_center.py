"""government template center

Revision ID: 0016_template_center
Revises: 0015_digital_dossier
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0016_template_center"
down_revision = "0015_digital_dossier"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document_templates", sa.Column("category", sa.String(length=100), nullable=False, server_default="GENERAL"))
    op.add_column("document_templates", sa.Column("official_number_prefix", sa.String(length=100), nullable=True))
    op.add_column("document_templates", sa.Column("variable_schema", sa.Text(), nullable=True))
    op.add_column("document_templates", sa.Column("checksum_sha256", sa.String(length=128), nullable=True))
    op.add_column("document_templates", sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("document_templates", sa.Column("uploaded_at", sa.DateTime(), nullable=True))
    op.add_column("document_templates", sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.create_index("ix_document_templates_category", "document_templates", ["category"])
    op.create_index("ix_document_templates_is_default", "document_templates", ["is_default"])
    op.execute("UPDATE document_templates SET category='GOVERNMENT', is_default=true WHERE code LIKE 'TPL_%_V1'")


def downgrade() -> None:
    op.drop_index("ix_document_templates_is_default", table_name="document_templates")
    op.drop_index("ix_document_templates_category", table_name="document_templates")
    op.drop_column("document_templates", "is_default")
    op.drop_column("document_templates", "uploaded_at")
    op.drop_column("document_templates", "uploaded_by")
    op.drop_column("document_templates", "checksum_sha256")
    op.drop_column("document_templates", "variable_schema")
    op.drop_column("document_templates", "official_number_prefix")
    op.drop_column("document_templates", "category")
