import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-coder:30b")


class AsyncNetworkService:
    """
    سرویس مدیریت کلاینت‌های ناهمگام HTTP جهت ارتباط با Ollama و API های خارجی.
    از یک کلاینت یکپارچه استفاده می‌کند تا از هدررفت سوکت‌های سیستم جلوگیری شود.
    """

    _client: httpx.AsyncClient = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            limits = httpx.Limits(
                max_keepalive_connections=50,
                max_connections=200
            )
            timeout = httpx.Timeout(60.0)
            cls._client = httpx.AsyncClient(limits=limits, timeout=timeout)
        return cls._client

    @classmethod
    async def close_client(cls) -> None:
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None

    @classmethod
    async def call_ollama(cls, prompt: str) -> str:
        """
        ارسال درخواست به موتور Ollama و دریافت پاسخ مدل محلی
        بدون نیاز به اینترنت و بدون هزینه توکن
        """
        try:
            client = cls.get_client()
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="موتور Ollama در زمان مقرر پاسخ نداد."
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"خطای ارتباط با Ollama: {str(e)}"
            )

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