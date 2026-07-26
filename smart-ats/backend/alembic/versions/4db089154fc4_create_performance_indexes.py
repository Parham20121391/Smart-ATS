"""create_performance_indexes

Revision ID: 4db089154fc4
Revises: c28265922784
Create Date: 2026-07-26 17:36:34.612440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4db089154fc4'
down_revision: Union[str, Sequence[str], None] = 'c28265922784'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass

"""create_performance_indexes

Revision ID: 4db089154fc4
Revises: c28265922784
Create Date: 2026-07-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '4db089154fc4'
down_revision: Union[str, Sequence[str], None] = 'c28265922784'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ایندکس B-Tree برای فیلتر سریع بر اساس منبع آگهی
    op.execute("""
        CREATE INDEX idx_jobs_source_type ON jobs(source_type)
    """)

    # ایندکس جزئی فقط روی ردیف‌های مشکوک (integrity_flag = FALSE)
    op.execute("""
        CREATE INDEX idx_apps_flagged_integrity
        ON applications(integrity_flag)
        WHERE integrity_flag = FALSE
    """)

    # ایندکس GIN روی آرایه مهارت‌ها برای جستجوی معنایی
    op.execute("""
        CREATE INDEX idx_jobs_skills_array
        ON jobs USING gin(skills_required)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_jobs_skills_array")
    op.execute("DROP INDEX IF EXISTS idx_apps_flagged_integrity")
    op.execute("DROP INDEX IF EXISTS idx_jobs_source_type")
def downgrade() -> None:
    """Downgrade schema."""
    pass
