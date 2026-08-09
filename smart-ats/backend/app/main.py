import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.services.network import AsyncNetworkService
from app.services.pdf_parser import PDFParserService
from app.routers import jobs, applications
from app.middleware import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


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

# ثبت هندلرهای سراسری خطا
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

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
@app.post("/test/ollama", tags=["Health Check"])
async def test_ollama(prompt: str = "سلام، آیا آفلاین کار می‌کنی؟"):
    """
    تست ارتباط با موتور Ollama و مدل محلی qwen3-coder
    """
    response = await AsyncNetworkService.call_ollama(prompt)
    return {
        "status": "success",
        "model": "qwen3-coder:30b",
        "prompt": prompt,
        "response": response
    }
@app.post("/test/pdf-parser", tags=["Health Check"])
async def test_pdf_parser(file: UploadFile = File(...)):
    """
    تست استخراج متن از فایل PDF رزومه
    """
    file_bytes = await file.read()
    extracted_text = PDFParserService.extract_text_from_bytes(file_bytes)
    stats = PDFParserService.get_text_stats(extracted_text)
    return {
        "status": "success",
        "stats": stats,
        "preview": extracted_text[:500]
    }