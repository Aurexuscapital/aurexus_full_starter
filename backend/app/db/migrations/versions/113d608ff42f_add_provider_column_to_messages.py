"""Add provider column to messages

Revision ID: 113d608ff42f
Revises: 0844981e285f
Create Date: 2025-09-08 20:35:08.510936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '113d608ff42f'
down_revision: Union[str, Sequence[str], None] = '0844981e285f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('messages', sa.Column('provider', sa.String(length=24), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('messages', 'provider')
