from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from app.schemas.job import JobResponse

router = APIRouter(prefix="/api/v1", tags=["Jobs"])


@router.get("/jobs", response_model=List[JobResponse], status_code=status.HTTP_200_OK)
async def get_jobs(
    source_type: Optional[str] = Query(None, description="فیلتر بر اساس منبع آگهی کراول شده"),
    page: int = Query(1, ge=1, description="شماره صفحه"),
    limit: int = Query(10, le=100, description="تعداد آیتم در هر صفحه")
):
    """
    دریافت لیست آگهی‌های شغلی با قابلیت فیلترینگ پیشرفته و صفحه‌بندی.
    این اندپوینت به دلیل ترافیک بالا پشت لایه کشینگ Redis قرار می‌گیرد.
    """
    # در فاز بعدی به دیتابیس متصل می‌شود
    return []