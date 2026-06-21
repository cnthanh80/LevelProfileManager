"""soft delete level profiles

Revision ID: 0028_soft_delete_profiles
Revises: 0027_enterprise_v40
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0028_soft_delete_profiles"
down_revision = "0027_enterprise_v40"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("level_profiles", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("level_profiles", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("level_profiles", sa.Column("deleted_by", sa.Integer(), nullable=True))
    op.create_foreign_key("level_profiles_deleted_by_fkey", "level_profiles", "users", ["deleted_by"], ["id"])
    op.create_index("ix_level_profiles_is_deleted", "level_profiles", ["is_deleted"])


def downgrade():
    op.drop_index("ix_level_profiles_is_deleted", table_name="level_profiles")
    op.drop_constraint("level_profiles_deleted_by_fkey", "level_profiles", type_="foreignkey")
    op.drop_column("level_profiles", "deleted_by")
    op.drop_column("level_profiles", "deleted_at")
    op.drop_column("level_profiles", "is_deleted")
