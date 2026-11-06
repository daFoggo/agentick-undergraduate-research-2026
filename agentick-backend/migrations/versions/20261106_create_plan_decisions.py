"""decisions on plan items (approve, reject, undo), append-only

Revision ID: c3d8f1a52e96
Revises: 9b4e2a7c1d30
Create Date: 2026-11-06 21:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c3d8f1a52e96'
down_revision: Union[str, None] = '9b4e2a7c1d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW = sa.text('now()')


def upgrade() -> None:
    op.create_table(
        'plan_decisions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('plan_id', sa.Uuid(), nullable=False),
        sa.Column('work_item_id', sa.Uuid(), nullable=False),
        sa.Column('event', sa.String(length=16), nullable=False),
        sa.Column('decided_by', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name=op.f('plan_decisions_plan_id_fkey'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('plan_decisions_pkey')),
    )
    op.create_index('plan_decisions_item_idx', 'plan_decisions', ['plan_id', 'work_item_id'])


def downgrade() -> None:
    op.drop_index('plan_decisions_item_idx', table_name='plan_decisions')
    op.drop_table('plan_decisions')
