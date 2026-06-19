"""multi organization management

Revision ID: 0014_multi_org
Revises: 0013_security_hardening
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0014_multi_org"
down_revision = "0013_security_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("parent_id", sa.Integer(), nullable=True))
    op.add_column("organizations", sa.Column("level", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("organizations", sa.Column("path", sa.String(length=500), nullable=True))
    op.add_column("organizations", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("organizations", sa.Column("manager_name", sa.String(length=255), nullable=True))
    op.add_column("organizations", sa.Column("contact_email", sa.String(length=255), nullable=True))
    op.create_foreign_key(
        "fk_organizations_parent_id",
        "organizations",
        "organizations",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_organizations_parent_id", "organizations", ["parent_id"])
    op.create_index("ix_organizations_path", "organizations", ["path"])
    op.execute("UPDATE organizations SET level = 1 WHERE level IS NULL")
    op.execute("UPDATE organizations SET path = '/' || code WHERE path IS NULL")


def downgrade() -> None:
    op.drop_index("ix_organizations_path", table_name="organizations")
    op.drop_index("ix_organizations_parent_id", table_name="organizations")
    op.drop_constraint("fk_organizations_parent_id", "organizations", type_="foreignkey")
    op.drop_column("organizations", "contact_email")
    op.drop_column("organizations", "manager_name")
    op.drop_column("organizations", "is_active")
    op.drop_column("organizations", "path")
    op.drop_column("organizations", "level")
    op.drop_column("organizations", "parent_id")
