from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    رهگیری تمام خطاهای HTTP و تبدیل به پاسخ JSON استاندارد
    """
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    رهگیری خطاهای اعتبارسنجی Pydantic و تبدیل به پاسخ ۴۰۰ خوانا
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"]
        })

    logger.warning(f"Validation Error | Path: {request.url.path} | Errors: {errors}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": True,
            "status_code": 400,
            "message": "داده‌های ورودی نامعتبر هستند.",
            "details": errors,
            "path": str(request.url.path)
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    رهگیری تمام خطاهای پیش‌بینی‌نشده - جلوگیری از نشت اطلاعات داخلی
    """
    logger.error(f"Unexpected Error | Path: {request.url.path} | Error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "خطای داخلی سرور. لطفاً با پشتیبانی تماس بگیرید.",
            "path": str(request.url.path)
        }
    )