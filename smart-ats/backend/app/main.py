import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.network import AsyncNetworkService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # راه‌اندازی کلاینت ناهمگام هنگام شروع سرور
    AsyncNetworkService.get_client()
    yield
    # بستن کلاینت هنگام خاموش شدن سرور
    await AsyncNetworkService.close_client()


app = FastAPI(
    title="Smart ATS API",
    description="سیستم هوشمند فرامرزی تجمیع‌کننده و راستی‌آزمایی جذب و استخدام",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Health Check"])
async def root():
    """
    بررسی سلامت سرور و Event Loop ناهمگام
    """
    loop = asyncio.get_event_loop()
    return {
        "status": "online",
        "system": "Smart ATS",
        "async_support": True,
        "event_loop_running": loop.is_running()
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    تایید آماده بودن کلاینت ناهمگام HTTP
    """
    client = AsyncNetworkService.get_client()
    return {
        "status": "healthy",
        "http_client": "ready",
        "client_closed": client.is_closed
    }