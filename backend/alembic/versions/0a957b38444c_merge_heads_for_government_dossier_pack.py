"""merge heads for government dossier pack

Revision ID: 0a957b38444c
Revises: 0028_gov_dossier_pack, 0028_soft_delete_profiles
Create Date: 2026-06-22 15:50:34.533482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0a957b38444c'
down_revision: Union[str, None] = ('0028_gov_dossier_pack', '0028_soft_delete_profiles')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
