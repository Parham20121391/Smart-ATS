"""create_enum_types

Revision ID: 3743b9171948
Revises: 
Create Date: 2026-07-26 16:43:04.813194

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3743b9171948'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TYPE job_source_enum AS ENUM (
            'INTERNAL',
            'LINKEDIN',
            'GOOGLE',
            'JOBINJA',
            'QUERA'
        )
    """)

    op.execute("""
        CREATE TYPE application_status_enum AS ENUM (
            'REGISTERED',
            'PENDING_VERIFICATION',
            'SCREENING',
            'TECH_INTERVIEW',
            'HR_INTERVIEW',
            'OFFER_EXTENDED',
            'HIRED',
            'REJECTED',
            'FLAGGED_REJECTED'
        )
    """)


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS application_status_enum")
    op.execute("DROP TYPE IF EXISTS job_source_enum")