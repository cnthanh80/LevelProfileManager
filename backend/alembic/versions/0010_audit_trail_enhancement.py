"""audit trail enhancement

Revision ID: 0010_audit_trail_enhancement
Revises: 0009_periodic_review_engine
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_audit_trail_enhancement"
down_revision = "0009_periodic_review_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_logs", sa.Column("request_id", sa.String(length=64), nullable=True))
    op.add_column("audit_logs", sa.Column("http_method", sa.String(length=20), nullable=True))
    op.add_column("audit_logs", sa.Column("path", sa.String(length=500), nullable=True))
    op.add_column("audit_logs", sa.Column("status_code", sa.Integer(), nullable=True))
    op.add_column("audit_logs", sa.Column("duration_ms", sa.Integer(), nullable=True))
    op.add_column("audit_logs", sa.Column("success", sa.Boolean(), nullable=True))
    op.add_column("audit_logs", sa.Column("source", sa.String(length=50), nullable=True, server_default="API"))
    op.create_index(op.f("ix_audit_logs_request_id"), "audit_logs", ["request_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_http_method"), "audit_logs", ["http_method"], unique=False)
    op.create_index(op.f("ix_audit_logs_path"), "audit_logs", ["path"], unique=False)
    op.create_index(op.f("ix_audit_logs_status_code"), "audit_logs", ["status_code"], unique=False)
    op.create_index(op.f("ix_audit_logs_success"), "audit_logs", ["success"], unique=False)
    op.create_index(op.f("ix_audit_logs_source"), "audit_logs", ["source"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_source"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_success"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_status_code"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_path"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_http_method"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_request_id"), table_name="audit_logs")
    op.drop_column("audit_logs", "source")
    op.drop_column("audit_logs", "success")
    op.drop_column("audit_logs", "duration_ms")
    op.drop_column("audit_logs", "status_code")
    op.drop_column("audit_logs", "path")
    op.drop_column("audit_logs", "http_method")
    op.drop_column("audit_logs", "request_id")
