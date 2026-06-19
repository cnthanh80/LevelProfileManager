"""initial core schema

Revision ID: 0001_initial_core_schema
Revises: 
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_core_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("org_type", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_organizations_id", "organizations", ["id"])
    op.create_index("ix_organizations_code", "organizations", ["code"])

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_roles_id", "roles", ["id"])
    op.create_index("ix_roles_code", "roles", ["code"])

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=True, unique=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "information_systems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("operator_org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("manager_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("main_functions", sa.Text(), nullable=True),
        sa.Column("user_groups", sa.Text(), nullable=True),
        sa.Column("data_types", sa.Text(), nullable=True),
        sa.Column("importance_level", sa.String(length=100), nullable=True),
        sa.Column("deployment_model", sa.String(length=50), nullable=True),
        sa.Column("environment", sa.String(length=50), nullable=True),
        sa.Column("operation_status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("proposed_level", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_information_systems_id", "information_systems", ["id"])
    op.create_index("ix_information_systems_code", "information_systems", ["code"])

    op.create_table(
        "level_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_code", sa.String(length=100), nullable=False, unique=True),
        sa.Column("information_system_id", sa.Integer(), sa.ForeignKey("information_systems.id"), nullable=False),
        sa.Column("proposed_level", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False, server_default="DRAFT"),
        sa.Column("basis_for_level", sa.Text(), nullable=True),
        sa.Column("system_scope_description", sa.Text(), nullable=True),
        sa.Column("technical_architecture", sa.Text(), nullable=True),
        sa.Column("confidentiality_impact", sa.Text(), nullable=True),
        sa.Column("integrity_impact", sa.Text(), nullable=True),
        sa.Column("availability_impact", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("locked_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_level_profiles_id", "level_profiles", ["id"])
    op.create_index("ix_level_profiles_profile_code", "level_profiles", ["profile_code"])
    op.create_index("ix_level_profiles_status", "level_profiles", ["status"])

    op.create_table(
        "profile_workflow_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("level_profiles.id"), nullable=False),
        sa.Column("from_status", sa.String(length=80), nullable=True),
        sa.Column("to_status", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_profile_workflow_history_id", "profile_workflow_history", ["id"])
    op.create_index("ix_profile_workflow_history_profile_id", "profile_workflow_history", ["profile_id"])


def downgrade() -> None:
    op.drop_table("profile_workflow_history")
    op.drop_table("level_profiles")
    op.drop_table("information_systems")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("organizations")
