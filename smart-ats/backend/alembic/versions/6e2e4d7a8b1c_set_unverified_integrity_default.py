"""set_unverified_integrity_default

Revision ID: 6e2e4d7a8b1c
Revises: 4db089154fc4
Create Date: 2026-09-15
"""
from typing import Sequence, Union
from alembic import op

revision: str = '6e2e4d7a8b1c'
down_revision: Union[str, Sequence[str], None] = '4db089154fc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE applications ALTER COLUMN integrity_flag SET DEFAULT FALSE")


def downgrade() -> None:
    op.execute("ALTER TABLE applications ALTER COLUMN integrity_flag SET DEFAULT TRUE")
