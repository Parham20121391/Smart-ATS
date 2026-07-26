"""create_companies_and_candidates_tables

Revision ID: 21ca1d3c9f5d
Revises: 3743b9171948
Create Date: 2026-07-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '21ca1d3c9f5d'
down_revision: Union[str, Sequence[str], None] = '3743b9171948'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE companies (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            industry VARCHAR(150),
            website VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE candidates (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(50),
            github_username VARCHAR(100),
            linkedin_profile_url VARCHAR(2048),
            resume_url VARCHAR(2048) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS candidates")
    op.execute("DROP TABLE IF EXISTS companies")