"""real digital signature gateway foundation

Revision ID: 0020_real_signature
Revises: 0019_ai_level_rec
Create Date: 2026-06-20 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0020_real_signature"
down_revision = "0019_ai_level_rec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "signature_providers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("provider_type", sa.String(length=50), nullable=False, server_default="REMOTE_SIGNING"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column("endpoint_url", sa.String(length=1000), nullable=True),
        sa.Column("callback_url", sa.String(length=1000), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_signature_providers_id"), "signature_providers", ["id"], unique=False)
    op.create_index(op.f("ix_signature_providers_code"), "signature_providers", ["code"], unique=True)
    op.create_index(op.f("ix_signature_providers_status"), "signature_providers", ["status"], unique=False)

    op.create_table(
        "signature_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=True),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("request_code", sa.String(length=80), nullable=False),
        sa.Column("sign_method", sa.String(length=50), nullable=False, server_default="REMOTE_SIGNING"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="CREATED"),
        sa.Column("document_hash", sa.String(length=128), nullable=False),
        sa.Column("request_payload_json", sa.Text(), nullable=True),
        sa.Column("provider_response_json", sa.Text(), nullable=True),
        sa.Column("callback_payload_json", sa.Text(), nullable=True),
        sa.Column("external_transaction_id", sa.String(length=255), nullable=True),
        sa.Column("signed_hash", sa.String(length=128), nullable=True),
        sa.Column("signed_file_path", sa.String(length=1000), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["level_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_id"], ["signature_providers.id"]),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["version_id"], ["profile_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_code"),
    )
    op.create_index(op.f("ix_signature_requests_id"), "signature_requests", ["id"], unique=False)
    op.create_index(op.f("ix_signature_requests_profile_id"), "signature_requests", ["profile_id"], unique=False)
    op.create_index(op.f("ix_signature_requests_version_id"), "signature_requests", ["version_id"], unique=False)
    op.create_index(op.f("ix_signature_requests_status"), "signature_requests", ["status"], unique=False)
    op.create_index(op.f("ix_signature_requests_request_code"), "signature_requests", ["request_code"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_signature_requests_request_code"), table_name="signature_requests")
    op.drop_index(op.f("ix_signature_requests_status"), table_name="signature_requests")
    op.drop_index(op.f("ix_signature_requests_version_id"), table_name="signature_requests")
    op.drop_index(op.f("ix_signature_requests_profile_id"), table_name="signature_requests")
    op.drop_index(op.f("ix_signature_requests_id"), table_name="signature_requests")
    op.drop_table("signature_requests")
    op.drop_index(op.f("ix_signature_providers_status"), table_name="signature_providers")
    op.drop_index(op.f("ix_signature_providers_code"), table_name="signature_providers")
    op.drop_index(op.f("ix_signature_providers_id"), table_name="signature_providers")
    op.drop_table("signature_providers")
