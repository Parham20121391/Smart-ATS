# smart-ats/backend/app/middleware.py
import os
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from fastapi import Request, Response, status, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# ۱. هندلر خطاهای HTTP که main.py ایمپورت کرده
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ۲. هندلر اعتبارسنجی ورودی Pydantic که main.py ایمپورت کرده
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# ۳. هندلر سراسری خطاهای سرور که main.py ایمپورت کرده
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "خطای داخلی سرور رخ داده است."}
    )

# ۴. گارد امنیتی API Key که main.py ایمپورت کرده
async def require_api_key(api_key: Optional[str] = Security(api_key_header)):
    expected_api_key = os.getenv("INTERNAL_API_KEY", "smart_ats_internal_secret_key")
    if not api_key or api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کلید API نامعتبر یا یافت نشد."
        )
    return api_key

# ۵. لایه محدودسازی نرخ درخواست (Rate Limiting)
class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        self.rate_limits: Dict[str, Dict[str, int]] = {
            "/api/v1/applications": {
                "method": "POST",
                "limit": 3,
                "window": 60
            }
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        method = request.method

        rule = self.rate_limits.get(path)
        if rule and rule["method"] == method:
            client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
            redis_key = f"rate_limit:{client_ip}:{path}"

            try:
                current_requests = await self.redis.incr(redis_key)
                if current_requests == 1:
                    await self.redis.expire(redis_key, rule["window"])

                if current_requests > rule["limit"]:
                    ttl = await self.redis.ttl(redis_key)
                    retry_after = ttl if ttl > 0 else rule["window"]
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید.",
                            "detail": f"حداکثر {rule['limit']} درخواست در هر دقیقه مجاز است."
                        },
                        headers={"Retry-After": str(retry_after)}
                    )
            except Exception:
                pass

        return await call_next(request)