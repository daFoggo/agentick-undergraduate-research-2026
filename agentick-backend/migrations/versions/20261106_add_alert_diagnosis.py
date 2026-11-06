"""alerts carry the diagnosis card (hypotheses with evidence, missing info, action)

Revision ID: 5a7d3e91b2c4
Revises: e8c1b47a2f05
Create Date: 2026-11-06 12:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '5a7d3e91b2c4'
down_revision: Union[str, None] = 'e8c1b47a2f05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('diagnosis', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('alerts', 'diagnosis')
