"""create posts table

Revision ID: 83c799f497e4
Revises: 
Create Date: 2025-04-07 14:48:39.268170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83c799f497e4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable=False, primary_key=True), sa.Column('title', sa.String(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('posts')
