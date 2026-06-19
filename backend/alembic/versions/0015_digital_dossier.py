"""digital signature and electronic dossier

Revision ID: 0015_digital_dossier
Revises: 0014_multi_org
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0015_digital_dossier"
down_revision = "0014_multi_org"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profile_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("snapshot_hash", sa.String(length=128), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_profile_versions_profile_id", "profile_versions", ["profile_id"])
    op.create_index("ix_profile_versions_snapshot_hash", "profile_versions", ["snapshot_hash"])
    op.create_unique_constraint("uq_profile_versions_profile_version", "profile_versions", ["profile_id", "version_no"])

    op.create_table(
        "profile_signatures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", sa.Integer(), sa.ForeignKey("profile_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("signer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("signer_name", sa.String(length=255), nullable=False),
        sa.Column("signer_role", sa.String(length=100), nullable=True),
        sa.Column("sign_method", sa.String(length=50), nullable=False, server_default="MOCK"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="SIGNED"),
        sa.Column("signature_hash", sa.String(length=128), nullable=False),
        sa.Column("certificate_subject", sa.String(length=500), nullable=True),
        sa.Column("signed_file_path", sa.String(length=1000), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_profile_signatures_profile_id", "profile_signatures", ["profile_id"])
    op.create_index("ix_profile_signatures_version_id", "profile_signatures", ["version_id"])
    op.create_index("ix_profile_signatures_signature_hash", "profile_signatures", ["signature_hash"])
    op.create_index("ix_profile_signatures_status", "profile_signatures", ["status"])


def downgrade() -> None:
    op.drop_table("profile_signatures")
    op.drop_table("profile_versions")
