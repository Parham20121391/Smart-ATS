import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.network import AsyncNetworkService
from app.routers import jobs, applications


@asynccontextmanager
async def lifespan(app: FastAPI):
    AsyncNetworkService.get_client()
    yield
    await AsyncNetworkService.close_client()


app = FastAPI(
    title="Smart ATS API",
    description="سیستم هوشمند فرامرزی تجمیع‌کننده و راستی‌آزمایی جذب و استخدام",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(jobs.router)
app.include_router(applications.router)


@app.get("/", tags=["Health Check"])
async def root():
    loop = asyncio.get_event_loop()
    return {
        "status": "online",
        "system": "Smart ATS",
        "async_support": True,
        "event_loop_running": loop.is_running()
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    client = AsyncNetworkService.get_client()
    return {
        "status": "healthy",
        "http_client": "ready",
        "client_closed": client.is_closed
    }