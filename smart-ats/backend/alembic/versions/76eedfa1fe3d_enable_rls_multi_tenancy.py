"""enable_rls_multi_tenancy

Revision ID: 76eedfa1fe3d
Revises: 4db089154fc4
Create Date: 2026-11-12 14:50:00.000000

"""
from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '76eedfa1fe3d'
down_revision: Union[str, None] = '4db089154fc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ۱. فعال‌سازی RLS روی جدول آگهی‌های شغلی (jobs) بر اساس company_id
    op.execute("ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE jobs FORCE ROW LEVEL SECURITY;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_jobs_policy ON jobs;")
    op.execute("""
        CREATE POLICY tenant_isolation_jobs_policy ON jobs
        AS RESTRICTIVE
        USING (
            company_id = NULLIF(current_setting('app.current_company_id', true), '')::INTEGER
        )
        WITH CHECK (
            company_id = NULLIF(current_setting('app.current_company_id', true), '')::INTEGER
        );
    """)

    # ۲. فعال‌سازی RLS روی جدول درخواست‌های استخدامی (applications) از طریق کلید خارجی job_id
    op.execute("ALTER TABLE applications ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE applications FORCE ROW LEVEL SECURITY;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_applications_policy ON applications;")
    op.execute("""
        CREATE POLICY tenant_isolation_applications_policy ON applications
        AS RESTRICTIVE
        USING (
            job_id IN (
                SELECT id FROM jobs
                WHERE company_id = NULLIF(current_setting('app.current_company_id', true), '')::INTEGER
            )
        )
        WITH CHECK (
            job_id IN (
                SELECT id FROM jobs
                WHERE company_id = NULLIF(current_setting('app.current_company_id', true), '')::INTEGER
            )
        );
    """)

    # ۳. فعال‌سازی RLS روی جدول متقاضیان (candidates) برای نمایش صرفاً کاندیداهای مرتبط با آگهی‌های شرکت
    op.execute("ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE candidates FORCE ROW LEVEL SECURITY;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_candidates_policy ON candidates;")
    op.execute("""
        CREATE POLICY tenant_isolation_candidates_policy ON candidates
        AS RESTRICTIVE
        USING (
            id IN (
                SELECT a.candidate_id FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE j.company_id = NULLIF(current_setting('app.current_company_id', true), '')::INTEGER
            )
        )
        WITH CHECK (true);
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_candidates_policy ON candidates;")
    op.execute("ALTER TABLE candidates NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE candidates DISABLE ROW LEVEL SECURITY;")

    op.execute("DROP POLICY IF EXISTS tenant_isolation_applications_policy ON applications;")
    op.execute("ALTER TABLE applications NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE applications DISABLE ROW LEVEL SECURITY;")

    op.execute("DROP POLICY IF EXISTS tenant_isolation_jobs_policy ON jobs;")
    op.execute("ALTER TABLE jobs NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE jobs DISABLE ROW LEVEL SECURITY;")