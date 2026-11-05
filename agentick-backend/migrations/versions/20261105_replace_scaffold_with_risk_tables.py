"""replace the scaffold items/users tables with the alert and similar-case tables

Plane owns accounts and the work items, so this backend drops its own users table and the demo items table and keeps
only what the sprint-risk services publish and decide.

Revision ID: 3c1f9d7a2b45
Revises: aa2715ade99b
Create Date: 2026-11-05 15:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '3c1f9d7a2b45'
down_revision: Union[str, None] = 'aa2715ade99b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW = sa.text('now()')


def upgrade() -> None:
    op.drop_table('users')
    op.drop_table('items')
    op.create_table(
        'alerts',
        sa.Column('work_item_id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('issue_key', sa.String(length=32), nullable=False),
        sa.Column('comment_id', sa.Uuid(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('inactive_days', sa.Float(), nullable=False),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.PrimaryKeyConstraint('work_item_id', name=op.f('alerts_pkey')),
    )
    op.create_table(
        'alert_decisions',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('work_item_id', sa.Uuid(), nullable=False),
        sa.Column('event', sa.String(length=16), nullable=False),
        sa.Column('decided_by', sa.String(length=255), nullable=False),
        sa.Column('prev_priority', sa.String(length=16), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.ForeignKeyConstraint(['work_item_id'], ['alerts.work_item_id'],
                                name=op.f('alert_decisions_work_item_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('alert_decisions_pkey')),
    )
    op.create_index(op.f('work_item_id_idx'), 'alert_decisions', ['work_item_id'])
    op.create_table(
        'similar_cases',
        sa.Column('work_item_id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('sizes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('project_size', sa.Integer(), nullable=False),
        sa.Column('cases', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.PrimaryKeyConstraint('work_item_id', name=op.f('similar_cases_pkey')),
    )


def downgrade() -> None:
    op.drop_table('similar_cases')
    op.drop_index(op.f('work_item_id_idx'), table_name='alert_decisions')
    op.drop_table('alert_decisions')
    op.drop_table('alerts')
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('items_pkey')),
        sa.UniqueConstraint('name', name=op.f('items_name_key')),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), server_default='member', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=NOW, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('users_pkey')),
        sa.UniqueConstraint('email', name=op.f('users_email_key')),
    )
