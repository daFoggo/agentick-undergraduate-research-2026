"""alerts remember how much of the sprint had passed when they were raised

Revision ID: c3a8f15e7d92
Revises: 7b4e2c9d1a60
Create Date: 2026-11-05 19:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c3a8f15e7d92'
down_revision: Union[str, None] = '7b4e2c9d1a60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('mark', sa.Float(), nullable=False, server_default='0.5'))


def downgrade() -> None:
    op.drop_column('alerts', 'mark')
