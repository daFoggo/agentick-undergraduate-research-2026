"""alerts remember the Plane users the work item is assigned to (for the "Your work" list)

Revision ID: 7c2f9d40a1b8
Revises: 5a7d3e91b2c4
Create Date: 2026-11-06 18:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '7c2f9d40a1b8'
down_revision: Union[str, None] = '5a7d3e91b2c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('assignee_ids', postgresql.JSONB(astext_type=sa.Text()),
                                      nullable=False, server_default='[]'))


def downgrade() -> None:
    op.drop_column('alerts', 'assignee_ids')
