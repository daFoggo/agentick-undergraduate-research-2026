"""alerts carry the diagnosed cause of being stuck and the quote behind it

Revision ID: e8c1b47a2f05
Revises: d5b90a3e4c18
Create Date: 2026-11-05 21:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e8c1b47a2f05'
down_revision: Union[str, None] = 'd5b90a3e4c18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('cause', sa.String(24), nullable=True))
    op.add_column('alerts', sa.Column('evidence_quote', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('alerts', 'evidence_quote')
    op.drop_column('alerts', 'cause')
