from contextvars import ContextVar
from typing import Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session, with_loader_criteria
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# تسک SAP-74: نگهداری شناسه مستأجر (شرکت) فعلی در سطح کانتکست هر درخواست ناهمگام
current_tenant_id: ContextVar[Optional[int]] = ContextVar("current_tenant_id", default=None)


def set_current_tenant(company_id: Optional[int]):
    """تنظیم شناسه شرکت جاری در کانتکست اپلیکیشن"""
    return current_tenant_id.set(company_id)


def reset_current_tenant(token) -> None:
    """بازنشانی کانتکست مستأجر پس از پایان درخواست"""
    current_tenant_id.reset(token)


def get_current_tenant() -> Optional[int]:
    """دریافت شناسه شرکت جاری"""
    return current_tenant_id.get()


class Base(DeclarativeBase):
    pass


# تسک SAP-74 (لایه ۱): فیلتر خودکار تمامی کوئری‌های SELECT لایه ORM بر اساس company_id مستأجر فعلی
@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_orm_filter(execute_state):
    tenant_id = get_current_tenant()
    if (
        tenant_id is not None
        and execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
    ):
        from app.models.job import Job

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                Job,
                lambda cls: cls.company_id == tenant_id,
                include_aliases=True,
            )
        )


# تسک SAP-74 (لایه ۲): همگام‌سازی خودکار متغیر نشست PostgreSQL RLS در شروع هر تراکنش
@event.listens_for(Session, "after_begin")
def _set_postgres_rls_tenant(session, transaction, connection):
    tenant_id = get_current_tenant()
    if tenant_id is not None:
        connection.execute(
            text("SET LOCAL app.current_company_id = :tenant_id"),
            {"tenant_id": str(tenant_id)},
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()