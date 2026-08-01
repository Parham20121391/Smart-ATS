import httpx
from fastapi import HTTPException, status


class AsyncNetworkService:
    """
    سرویس مدیریت کلاینت‌های ناهمگام HTTP جهت ارتباط با Ollama و API های خارجی.
    از یک کلاینت یکپارچه استفاده می‌کند تا از هدررفت سوکت‌های سیستم جلوگیری شود.
    """

    _client: httpx.AsyncClient = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            # تنظیم محدودیت‌های اتصال متناسب با پردازش‌های سنگین
            limits = httpx.Limits(
                max_keepalive_connections=50,
                max_connections=200
            )
            # تنظیم تایم‌اوت‌های طولانی برای پردازش‌های سنگین هوش مصنوعی
            timeout = httpx.Timeout(60.0)
            cls._client = httpx.AsyncClient(limits=limits, timeout=timeout)
        return cls._client

    @classmethod
    async def close_client(cls) -> None:
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None

    @classmethod
    async def safe_get(cls, url: str, headers: dict = None) -> dict:
        """
        اجرای امن درخواست GET ناهمگام با مدیریت خطا
        """
        try:
            client = cls.get_client()
            response = await client.get(url, headers=headers or {})
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="درخواست شبکه به دلیل تایم‌اوت ناموفق بود."
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"خطای لایه ناهمگام شبکه: {str(e)}"
            )