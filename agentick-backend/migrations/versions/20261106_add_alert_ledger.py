"""alerts count the runs that published them and remember the previous score

Revision ID: d5a1c7e49b02
Revises: c3d8f1a52e96
Create Date: 2026-11-06 22:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd5a1c7e49b02'
down_revision: Union[str, None] = 'c3d8f1a52e96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('seen_count', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('alerts', sa.Column('prev_score', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('alerts', 'prev_score')
    op.drop_column('alerts', 'seen_count')
