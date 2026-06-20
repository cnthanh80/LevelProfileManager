"""enterprise release v40

Revision ID: 0027_enterprise_v40
Revises: 0026_reporting_dw
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = "0027_enterprise_v40"
down_revision = "0026_reporting_dw"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "enterprise_configurations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("config_key", sa.String(length=120), nullable=False),
        sa.Column("config_group", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("config_value", sa.Text(), nullable=True),
        sa.Column("value_type", sa.String(length=40), nullable=False, server_default="STRING"),
        sa.Column("is_secret", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("config_key", name="uq_enterprise_config_key"),
    )
    op.create_index("ix_ec_key", "enterprise_configurations", ["config_key"])
    op.create_index("ix_ec_group", "enterprise_configurations", ["config_group"])
    op.create_index("ix_ec_enabled", "enterprise_configurations", ["is_enabled"])

    op.create_table(
        "enterprise_health_checks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("component_code", sa.String(length=120), nullable=False),
        sa.Column("component_name", sa.String(length=255), nullable=False),
        sa.Column("component_group", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="UNKNOWN"),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("checked_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ehc_component", "enterprise_health_checks", ["component_code"])
    op.create_index("ix_ehc_group", "enterprise_health_checks", ["component_group"])
    op.create_index("ix_ehc_status", "enterprise_health_checks", ["status"])
    op.create_index("ix_ehc_checked_at", "enterprise_health_checks", ["checked_at"])

    op.create_table(
        "enterprise_job_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("job_code", sa.String(length=120), nullable=False),
        sa.Column("job_name", sa.String(length=255), nullable=False),
        sa.Column("job_group", sa.String(length=80), nullable=False),
        sa.Column("schedule_expression", sa.String(length=120), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_hint", sa.String(length=120), nullable=True),
        sa.Column("last_status", sa.String(length=40), nullable=True),
        sa.Column("last_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("job_code", name="uq_enterprise_job_code"),
    )
    op.create_index("ix_ejs_code", "enterprise_job_schedules", ["job_code"])
    op.create_index("ix_ejs_group", "enterprise_job_schedules", ["job_group"])
    op.create_index("ix_ejs_enabled", "enterprise_job_schedules", ["is_enabled"])
    op.create_index("ix_ejs_status", "enterprise_job_schedules", ["last_status"])
    op.create_index("ix_ejs_last_run", "enterprise_job_schedules", ["last_run_at"])

    op.create_table(
        "data_retention_policies",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("policy_code", sa.String(length=120), nullable=False),
        sa.Column("data_domain", sa.String(length=120), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False, server_default="365"),
        sa.Column("archive_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("purge_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("legal_hold", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("policy_code", name="uq_retention_policy_code"),
    )
    op.create_index("ix_drp_code", "data_retention_policies", ["policy_code"])
    op.create_index("ix_drp_domain", "data_retention_policies", ["data_domain"])

    op.create_table(
        "backup_records",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("backup_code", sa.String(length=120), nullable=False),
        sa.Column("backup_type", sa.String(length=60), nullable=False, server_default="LOGICAL"),
        sa.Column("scope", sa.String(length=120), nullable=False, server_default="DATABASE"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="COMPLETED"),
        sa.Column("storage_location", sa.String(length=500), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("size_mb", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("validated_at", sa.DateTime(), nullable=True),
        sa.Column("validation_status", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("backup_code", name="uq_backup_record_code"),
    )
    op.create_index("ix_br_code", "backup_records", ["backup_code"])
    op.create_index("ix_br_type", "backup_records", ["backup_type"])
    op.create_index("ix_br_scope", "backup_records", ["scope"])
    op.create_index("ix_br_status", "backup_records", ["status"])
    op.create_index("ix_br_started", "backup_records", ["started_at"])
    op.create_index("ix_br_completed", "backup_records", ["completed_at"])
    op.create_index("ix_br_validated", "backup_records", ["validated_at"])
    op.create_index("ix_br_validation_status", "backup_records", ["validation_status"])


def downgrade():
    op.drop_table("backup_records")
    op.drop_table("data_retention_policies")
    op.drop_table("enterprise_job_schedules")
    op.drop_table("enterprise_health_checks")
    op.drop_table("enterprise_configurations")
