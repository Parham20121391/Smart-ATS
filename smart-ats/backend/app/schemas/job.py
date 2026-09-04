from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    skills_required: Optional[List[str]] = []
    status: str
    source_type: str
    original_url: Optional[str] = None
    company_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
class JobResponse(BaseModel):
    id: int
    company_id: int
    title: str
    description: str
    skills_required: List[str]
    status: str
    source_type: str
    original_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- کلاس جدید برای تسک‌های 110، 111 و 112 ---
class NormalizedJobSchema(BaseModel):
    """
    شمای استانداردسازی آگهی‌های شغلی کراول‌شده پیش از ورود به دیتابیس
    (تسک ۱۱۱ و ۱۱۲)
    """
    title: str = Field(..., description="عنوان استاندارد موقعیت شغلی")
    company_name: str = Field(..., description="نام شرکت منتشر دهنده")
    description: str = Field(..., description="متن کامل و پاک‌سازی شده شرح شغل")
    skills_required: List[str] = Field(..., description="آرایه‌ای از مهارت‌های فنی مورد نیاز")
    original_url: str = Field(..., description="آدرس منبع اصلی آگهی")

    @field_validator('skills_required')
    @classmethod
    def normalize_skills_lowercase(cls, v: List[str]) -> List[str]:
        """
        تبدیل تمام مهارت‌ها به حروف کوچک و حذف فاصله‌های اضافی جهت بهینه‌سازی ایندکس GIN
        """
        return [skill.lower().strip() for skill in v]