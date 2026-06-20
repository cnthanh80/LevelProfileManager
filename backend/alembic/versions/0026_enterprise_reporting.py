"""enterprise reporting data warehouse

Revision ID: 0026_reporting_dw
Revises: 0025_compliance_mon
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0026_reporting_dw"
down_revision = "0025_compliance_mon"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "enterprise_report_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("snapshot_code", sa.String(length=120), nullable=False),
        sa.Column("period_type", sa.String(length=30), nullable=False, server_default="MONTHLY"),
        sa.Column("period_label", sa.String(length=50), nullable=False),
        sa.Column("total_systems", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_profiles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level_1_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level_2_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level_3_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level_4_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level_5_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_compliance_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("high_risk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overdue_review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_findings_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assessment_cases_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("snapshot_code", name="uq_enterprise_report_snapshot_code"),
    )
    op.create_index("ix_ers_code", "enterprise_report_snapshots", ["snapshot_code"])
    op.create_index("ix_ers_period_type", "enterprise_report_snapshots", ["period_type"])
    op.create_index("ix_ers_period_label", "enterprise_report_snapshots", ["period_label"])
    op.create_index("ix_ers_generated_at", "enterprise_report_snapshots", ["generated_at"])
    op.create_index("ix_ers_score", "enterprise_report_snapshots", ["overall_compliance_score"])
    op.create_index("ix_ers_high_risk", "enterprise_report_snapshots", ["high_risk_count"])

    op.create_table(
        "data_warehouse_metrics",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("metric_code", sa.String(length=120), nullable=False),
        sa.Column("metric_group", sa.String(length=80), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("metric_value", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dimension_key", sa.String(length=80), nullable=True),
        sa.Column("dimension_value", sa.String(length=255), nullable=True),
        sa.Column("measured_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_dwm_code", "data_warehouse_metrics", ["metric_code"])
    op.create_index("ix_dwm_group", "data_warehouse_metrics", ["metric_group"])
    op.create_index("ix_dwm_dimension_key", "data_warehouse_metrics", ["dimension_key"])
    op.create_index("ix_dwm_dimension_value", "data_warehouse_metrics", ["dimension_value"])
    op.create_index("ix_dwm_measured_at", "data_warehouse_metrics", ["measured_at"])

    op.create_table(
        "report_export_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("job_code", sa.String(length=120), nullable=False),
        sa.Column("report_type", sa.String(length=80), nullable=False),
        sa.Column("export_format", sa.String(length=20), nullable=False, server_default="CSV"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="COMPLETED"),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("job_code", name="uq_report_export_jobs_code"),
    )
    op.create_index("ix_rej_code", "report_export_jobs", ["job_code"])
    op.create_index("ix_rej_type", "report_export_jobs", ["report_type"])
    op.create_index("ix_rej_format", "report_export_jobs", ["export_format"])
    op.create_index("ix_rej_status", "report_export_jobs", ["status"])
    op.create_index("ix_rej_requested_by", "report_export_jobs", ["requested_by"])
    op.create_index("ix_rej_generated_at", "report_export_jobs", ["generated_at"])


def downgrade():
    op.drop_table("report_export_jobs")
    op.drop_table("data_warehouse_metrics")
    op.drop_table("enterprise_report_snapshots")
