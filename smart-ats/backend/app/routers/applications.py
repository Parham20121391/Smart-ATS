from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status
from app.schemas.application import ApplicationCreateResponse, VerificationResponse

router = APIRouter(prefix="/api/v1", tags=["Applications"])


@router.post("/applications", response_model=ApplicationCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_application(
    job_id: int = Query(..., description="شناسه آگهی شغلی"),
    github_username: str = Query(..., description="شناسه گیت‌هاب کارجو"),
    linkedin_url: str = Query(..., description="آدرس پروفایل لینکدین کارجو"),
    file: UploadFile = File(..., description="فایل رزومه PDF")
):
    """
    دریافت رزومه و اطلاعات کارجو.
    بلافاصله پس از ثبت، ورکرهای راستی‌آزمایی گیت‌هاب و لینکدین
    در بک‌گراند تریگر می‌شوند.
    """
    # در فاز بعدی پایپلاین کامل پیاده‌سازی می‌شود
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="پایپلاین پردازش رزومه در فاز بعدی پیاده‌سازی می‌شود."
    )


@router.get("/applications/verification/{id}", response_model=VerificationResponse, status_code=status.HTTP_200_OK)
async def get_application_verification(
    id: int
):
    """
    دریافت نمرات تفکیکی اصالت کارجو و وضعیت پرچم امنیتی
    جهت بررسی‌های امنیتی توسط Tech Lead و HR.
    """
    # در فاز بعدی به دیتابیس متصل می‌شود
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="این اندپوینت در فاز بعدی به لایه راستی‌آزمایی متصل می‌شود."
    )