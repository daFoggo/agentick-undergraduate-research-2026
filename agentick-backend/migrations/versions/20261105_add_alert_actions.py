"""alerts carry the action to take and what a decision applied

Revision ID: 7b4e2c9d1a60
Revises: 3c1f9d7a2b45
Create Date: 2026-11-05 18:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '7b4e2c9d1a60'
down_revision: Union[str, None] = '3c1f9d7a2b45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('action_type', sa.String(24), nullable=False, server_default='raise_priority'))
    op.add_column('alerts', sa.Column('action_text', sa.String(2000), nullable=True))
    op.add_column('alert_decisions', sa.Column('applied_comment_id', sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column('alert_decisions', 'applied_comment_id')
    op.drop_column('alerts', 'action_text')
    op.drop_column('alerts', 'action_type')
