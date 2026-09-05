import json
from contextlib import contextmanager
from pydantic import ValidationError
from app.schemas.job import NormalizedJobSchema
from app.database import SessionLocal, Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY

# تلاش برای ایمپورت مدل‌های ORM. در صورتی که ساخته نشده باشند، از نگاشت محلی استفاده می‌کنیم
try:
    from app.models.job import Job
    from app.models.company import Company
except ImportError:
    class Company(Base):
        __tablename__ = "companies"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(255), nullable=False)
        
    class Job(Base):
        __tablename__ = "jobs"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        company_id = Column(Integer, ForeignKey("companies.id"))
        title = Column(String(255), nullable=False)
        description = Column(Text, nullable=False)
        skills_required = Column(ARRAY(String))
        source_type = Column(String(50))
        original_url = Column(String(2048))
        status = Column(String(50), default="ACTIVE")

@contextmanager
def get_db_context_manager():
    """
    تسک ۱۱۸: مدیریت تراکنش و نشست پایگاه داده به صورت امن
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

class JobNormalizerService:
    """
    سرویس پاک‌سازی و یکپارچه‌سازی آگهی‌های ناهمگون کراول شده از اینترنت
    """
    
    @classmethod
    async def process_and_save_raw_html(cls, raw_html: str, source: str):
        cleaned_text = raw_html.replace("<div>", "").replace("</div>", "").strip()
        
        # خروجی ماک شده هوش مصنوعی
        mock_llm_output = {
            "title": "Senior Backend Developer",
            "company_name": "Nextron Team",
            "description": cleaned_text if cleaned_text else "We are looking for a FastAPI expert...",
            "skills_required": ["Python", "FastAPI", "PostgreSQL"],
            "original_url": "https://linkedin.com/jobs/view/123456"
        }
        
        try:
            # اعتبارسنجی با Pydantic
            normalized_data = NormalizedJobSchema(**mock_llm_output)
            
            # تسک ۱۱۸ و ۱۱۹: باز کردن تراکنش امن و درج در دیتابیس
            with get_db_context_manager() as db:
                # بررسی وجود شرکت یا ایجاد آن
                company = db.query(Company).filter(Company.name == normalized_data.company_name).first()
                if not company:
                    company = Company(name=normalized_data.company_name)
                    db.add(company)
                    db.flush() # گرفتن آیدی شرکت قبل از کامیت
                
                # نگاشت آبجکت ORM موقعیت شغلی
                new_job = Job(
                    company_id=company.id,
                    title=normalized_data.title,
                    description=normalized_data.description,
                    skills_required=normalized_data.skills_required,
                    source_type=source.upper(),
                    original_url=normalized_data.original_url,
                    status="ACTIVE"
                )
                db.add(new_job)
                db.commit()
            
            return f"SUCCESS_DATA_NORMALIZED_AND_SAVED: {normalized_data.title}"
            
        except ValidationError as e:
            # تسک ۱۲۰: مدیریت خطاهای Pydantic
            print(f"ERROR_LOGGER_CRITICAL: Validation failed. Reason: {str(e)}")
            return "NORMALIZATION_FAILED_VALIDATION"
        except Exception as e:
            # تسک ۱۲۰: بلوک try/except جهت پایداری سیستم در برابر خطاهای دیتابیس
            print(f"ERROR_LOGGER_CRITICAL: Database transaction failed. Reason: {str(e)}")
            return "NORMALIZATION_FAILED_DB_ERROR"