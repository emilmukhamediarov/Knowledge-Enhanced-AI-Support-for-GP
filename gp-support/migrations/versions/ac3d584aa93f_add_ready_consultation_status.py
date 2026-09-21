"""add ready consultation status

Revision ID: ac3d584aa93f
Revises: 587048921b91
Create Date: 2026-09-21 17:17:37.578119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac3d584aa93f'
down_revision: Union[str, Sequence[str], None] = '587048921b91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "ALTER TYPE consultationstatus ADD VALUE IF NOT EXISTS 'ready'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
