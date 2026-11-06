"""sprint-level plans: which open issues to move to the next cycle

Revision ID: 9b4e2a7c1d30
Revises: 7c2f9d40a1b8
Create Date: 2026-11-06 20:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '9b4e2a7c1d30'
down_revision: Union[str, None] = '7c2f9d40a1b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW = sa.text('now()')


def upgrade() -> None:
    op.create_table(
        'plans',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('cycle_id', sa.Uuid(), nullable=False),
        sa.Column('next_cycle_id', sa.Uuid(), nullable=False),
        sa.Column('sprint_name', sa.String(length=255), nullable=False),
        sa.Column('mark', sa.Float(), nullable=False),
        sa.Column('open_count', sa.Integer(), nullable=False),
        sa.Column('history_sprints', sa.Integer(), nullable=False),
        sa.Column('unfinished_share', sa.Float(), nullable=False),
        sa.Column('expected_unfinished', sa.Float(), nullable=False),
        sa.Column('budget', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('plans_pkey')),
        sa.UniqueConstraint('cycle_id', name=op.f('plans_cycle_id_key')),
    )
    op.create_table(
        'plan_items',
        sa.Column('plan_id', sa.Uuid(), nullable=False),
        sa.Column('work_item_id', sa.Uuid(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('issue_key', sa.String(length=32), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('why', sa.String(length=16), nullable=False),
        sa.Column('cause', sa.String(length=24), nullable=True),
        sa.Column('reason', sa.String(length=400), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name=op.f('plan_items_plan_id_fkey'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('plan_id', 'work_item_id', name=op.f('plan_items_pkey')),
    )


def downgrade() -> None:
    op.drop_table('plan_items')
    op.drop_table('plans')
