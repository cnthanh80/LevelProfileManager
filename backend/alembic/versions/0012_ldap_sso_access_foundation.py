"""ldap sso access foundation

Revision ID: 0012_ldap_sso_access_foundation
Revises: 0011_document_template_engine
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_ldap_sso_access_foundation"
down_revision = "0011_document_template_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("auth_provider", sa.String(length=50), nullable=False, server_default="LOCAL"))
    op.add_column("users", sa.Column("external_id", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("is_local_auth_allowed", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.create_index(op.f("ix_users_external_id"), "users", ["external_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_external_id"), table_name="users")
    op.drop_column("users", "is_local_auth_allowed")
    op.drop_column("users", "external_id")
    op.drop_column("users", "auth_provider")
