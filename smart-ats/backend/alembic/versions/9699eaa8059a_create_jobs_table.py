"""create_jobs_table

Revision ID: 9699eaa8059a
Revises: 21ca1d3c9f5d
Create Date: 2026-07-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9699eaa8059a'
down_revision: Union[str, Sequence[str], None] = '21ca1d3c9f5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE jobs (
            id SERIAL PRIMARY KEY,
            company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            skills_required VARCHAR(100)[],
            status VARCHAR(50) DEFAULT 'ACTIVE' NOT NULL,
            source_type job_source_enum DEFAULT 'INTERNAL' NOT NULL,
            original_url VARCHAR(2048),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS jobs")