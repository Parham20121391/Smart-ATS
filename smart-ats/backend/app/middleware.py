# smart-ats/backend/app/middleware.py
import os
import time
from typing import Dict, Any
import redis.asyncio as aioredis
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# تسک ۶۱: توسعه کلاس RateLimiterMiddleware بر بستر ردیس
class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        # تسک ۶۴: قوانین محدودسازی؛ اندپوینت ارسال درخواست: ۳ درخواست در ۶۰ ثانیه
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
            # تسک ۶۲: ساخت کلید اختصاصی ردیس rate_limit:{client_ip}:{request.url.path}
            client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
            redis_key = f"rate_limit:{client_ip}:{path}"

            try:
                # تسک ۶۳: منطق اتمیک افزایش شمارنده و تنظیم انقضا
                current_requests = await self.redis.incr(redis_key)
                if current_requests == 1:
                    await self.redis.expire(redis_key, rule["window"])

                # تسک ۶۴ و ۶۰: صدور خطای ۴۲۹ با هدر Retry-After در صورت تخلف
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
                # Fail-open برای تضمین پایداری در صورت قطعی موقت ردیس
                pass

        return await call_next(request)