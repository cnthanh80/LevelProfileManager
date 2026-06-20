"""AI level recommendation engine

Revision ID: 0019_ai_level_rec
Revises: 0018_assessment_portal
Create Date: 2026-06-20 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0019_ai_level_rec"
down_revision = "0018_assessment_portal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_level_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("information_system_id", sa.Integer(), nullable=True),
        sa.Column("current_level", sa.Integer(), nullable=True),
        sa.Column("recommended_level", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_band", sa.String(length=30), nullable=False, server_default="LOW"),
        sa.Column("mismatch_status", sa.String(length=50), nullable=False, server_default="MATCH"),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("reasons_json", sa.Text(), nullable=True),
        sa.Column("evidence_json", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("recommended_actions_json", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["information_system_id"], ["information_systems.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["level_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_level_recommendations_id"), "ai_level_recommendations", ["id"], unique=False)
    op.create_index(op.f("ix_ai_level_recommendations_profile_id"), "ai_level_recommendations", ["profile_id"], unique=False)
    op.create_index(op.f("ix_ai_level_recommendations_information_system_id"), "ai_level_recommendations", ["information_system_id"], unique=False)
    op.create_index(op.f("ix_ai_level_recommendations_recommended_level"), "ai_level_recommendations", ["recommended_level"], unique=False)
    op.create_index(op.f("ix_ai_level_recommendations_risk_band"), "ai_level_recommendations", ["risk_band"], unique=False)
    op.create_index(op.f("ix_ai_level_recommendations_mismatch_status"), "ai_level_recommendations", ["mismatch_status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_level_recommendations_mismatch_status"), table_name="ai_level_recommendations")
    op.drop_index(op.f("ix_ai_level_recommendations_risk_band"), table_name="ai_level_recommendations")
    op.drop_index(op.f("ix_ai_level_recommendations_recommended_level"), table_name="ai_level_recommendations")
    op.drop_index(op.f("ix_ai_level_recommendations_information_system_id"), table_name="ai_level_recommendations")
    op.drop_index(op.f("ix_ai_level_recommendations_profile_id"), table_name="ai_level_recommendations")
    op.drop_index(op.f("ix_ai_level_recommendations_id"), table_name="ai_level_recommendations")
    op.drop_table("ai_level_recommendations")
