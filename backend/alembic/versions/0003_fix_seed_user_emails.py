"""fix seed user emails

Revision ID: 0003_fix_seed_user_emails
Revises: 0002_checklist_engine
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003_fix_seed_user_emails"
down_revision: Union[str, None] = "0002_checklist_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE users SET email = 'admin@example.com' WHERE username = 'admin' AND email = 'admin@example.local'")
    op.execute("UPDATE users SET email = 'attt@example.com' WHERE username = 'attt' AND email = 'attt@example.local'")


def downgrade() -> None:
    op.execute("UPDATE users SET email = 'admin@example.local' WHERE username = 'admin' AND email = 'admin@example.com'")
    op.execute("UPDATE users SET email = 'attt@example.local' WHERE username = 'attt' AND email = 'attt@example.com'")
