"""create_applications_table

Revision ID: c28265922784
Revises: 9699eaa8059a
Create Date: 2026-07-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c28265922784'
down_revision: Union[str, Sequence[str], None] = '9699eaa8059a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE applications (
            id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
            current_status application_status_enum DEFAULT 'REGISTERED' NOT NULL,
            score REAL DEFAULT 0.0,
            github_verification_score REAL DEFAULT 0.0,
            linkedin_match_status VARCHAR(100) DEFAULT 'UNVERIFIED',
            integrity_flag BOOLEAN DEFAULT TRUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            CONSTRAINT unique_job_candidate UNIQUE(job_id, candidate_id)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS applications")