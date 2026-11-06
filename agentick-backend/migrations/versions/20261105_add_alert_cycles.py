"""alerts carry the cycles a move_next_cycle action needs

Revision ID: d5b90a3e4c18
Revises: c3a8f15e7d92
Create Date: 2026-11-05 20:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd5b90a3e4c18'
down_revision: Union[str, None] = 'c3a8f15e7d92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('cycle_id', sa.Uuid(), nullable=True))
    op.add_column('alerts', sa.Column('target_cycle_id', sa.Uuid(), nullable=True))


def downgrade() -> None:
    op.drop_column('alerts', 'target_cycle_id')
    op.drop_column('alerts', 'cycle_id')
