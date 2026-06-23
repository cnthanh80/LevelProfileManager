"""government dossier pack

Revision ID: 0028_gov_dossier_pack
Revises: 0027_enterprise_v40
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0028_gov_dossier_pack"
down_revision = "0027_enterprise_v40"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "government_dossiers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("dossier_code", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="GENERATED"),
        sa.Column("package_filename", sa.String(length=500), nullable=False),
        sa.Column("package_path", sa.String(length=1000), nullable=False),
        sa.Column("package_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("included_evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("dossier_code", name="uq_government_dossiers_code"),
    )
    op.create_index("ix_gd_id", "government_dossiers", ["id"])
    op.create_index("ix_gd_profile_id", "government_dossiers", ["profile_id"])
    op.create_index("ix_gd_code", "government_dossiers", ["dossier_code"])
    op.create_index("ix_gd_version", "government_dossiers", ["version"])
    op.create_index("ix_gd_status", "government_dossiers", ["status"])
    op.create_index("ix_gd_checksum", "government_dossiers", ["checksum_sha256"])
    op.create_index("ix_gd_generated_by", "government_dossiers", ["generated_by"])

    op.create_table(
        "government_dossier_files",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("dossier_id", sa.Integer(), sa.ForeignKey("government_dossiers.id"), nullable=False),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("file_type", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=500), nullable=False),
        sa.Column("file_path", sa.String(length=1000), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_gdf_id", "government_dossier_files", ["id"])
    op.create_index("ix_gdf_dossier_id", "government_dossier_files", ["dossier_id"])
    op.create_index("ix_gdf_profile_id", "government_dossier_files", ["profile_id"])
    op.create_index("ix_gdf_file_type", "government_dossier_files", ["file_type"])
    op.create_index("ix_gdf_checksum", "government_dossier_files", ["checksum_sha256"])


def downgrade():
    op.drop_table("government_dossier_files")
    op.drop_table("government_dossiers")
