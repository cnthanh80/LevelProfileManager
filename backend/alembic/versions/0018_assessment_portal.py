"""assessment portal

Revision ID: 0018_assessment_portal
Revises: 0017_sla_risk
Create Date: 2026-06-20 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0018_assessment_portal"
down_revision = "0017_sla_risk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assessment_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_code", sa.String(length=100), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("assessment_unit", sa.String(length=255), nullable=True),
        sa.Column("contact_person", sa.String(length=255), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("submission_method", sa.String(length=60), nullable=False, server_default="PORTAL"),
        sa.Column("status", sa.String(length=60), nullable=False, server_default="DRAFT"),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["level_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_code"),
    )
    op.create_index(op.f("ix_assessment_cases_id"), "assessment_cases", ["id"], unique=False)
    op.create_index(op.f("ix_assessment_cases_case_code"), "assessment_cases", ["case_code"], unique=True)
    op.create_index(op.f("ix_assessment_cases_profile_id"), "assessment_cases", ["profile_id"], unique=False)
    op.create_index(op.f("ix_assessment_cases_status"), "assessment_cases", ["status"], unique=False)

    op.create_table(
        "assessment_feedbacks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("feedback_type", sa.String(length=60), nullable=False, server_default="COMMENT"),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False, server_default="OPEN"),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column("responded_by", sa.Integer(), nullable=True),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["assessment_cases.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["level_profiles.id"]),
        sa.ForeignKeyConstraint(["responded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessment_feedbacks_id"), "assessment_feedbacks", ["id"], unique=False)
    op.create_index(op.f("ix_assessment_feedbacks_case_id"), "assessment_feedbacks", ["case_id"], unique=False)
    op.create_index(op.f("ix_assessment_feedbacks_profile_id"), "assessment_feedbacks", ["profile_id"], unique=False)
    op.create_index(op.f("ix_assessment_feedbacks_status"), "assessment_feedbacks", ["status"], unique=False)
    op.create_index(op.f("ix_assessment_feedbacks_severity"), "assessment_feedbacks", ["severity"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_assessment_feedbacks_severity"), table_name="assessment_feedbacks")
    op.drop_index(op.f("ix_assessment_feedbacks_status"), table_name="assessment_feedbacks")
    op.drop_index(op.f("ix_assessment_feedbacks_profile_id"), table_name="assessment_feedbacks")
    op.drop_index(op.f("ix_assessment_feedbacks_case_id"), table_name="assessment_feedbacks")
    op.drop_index(op.f("ix_assessment_feedbacks_id"), table_name="assessment_feedbacks")
    op.drop_table("assessment_feedbacks")
    op.drop_index(op.f("ix_assessment_cases_status"), table_name="assessment_cases")
    op.drop_index(op.f("ix_assessment_cases_profile_id"), table_name="assessment_cases")
    op.drop_index(op.f("ix_assessment_cases_case_code"), table_name="assessment_cases")
    op.drop_index(op.f("ix_assessment_cases_id"), table_name="assessment_cases")
    op.drop_table("assessment_cases")
