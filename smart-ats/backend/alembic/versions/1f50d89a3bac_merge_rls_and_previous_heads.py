"""merge_rls_and_previous_heads

Revision ID: 1f50d89a3bac
Revises: 6e2e4d7a8b1c, 76eedfa1fe3d
Create Date: 2026-11-12 17:24:21.152378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f50d89a3bac'
down_revision: Union[str, Sequence[str], None] = ('6e2e4d7a8b1c', '76eedfa1fe3d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
