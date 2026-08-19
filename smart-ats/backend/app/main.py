import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.services.semantic_matching import SemanticMatchingEngine
from app.services.embedding_service import EmbeddingService
from app.services.network import AsyncNetworkService
from app.services.vector_db import VectorDBService
from app.services.pdf_parser import PDFParserService
from app.services.ai_service import OllamaAIService, ExtractedResumeSchema
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


@app.post("/test/ai-extract", tags=["Health Check"])
async def test_ai_extraction(file: UploadFile = File(...)):
    """
    تست کامل پایپ‌لاین: PDF → متن خام → Ollama → JSON ساختاریافته
    """
    file_bytes = await file.read()
    resume_text = PDFParserService.extract_text_from_bytes(file_bytes)
    extracted_data = await OllamaAIService.extract_resume_metadata(resume_text)
    footprint = OllamaAIService.check_digital_footprint(extracted_data)
    return {
        "status": "success",
        "extracted_data": extracted_data.model_dump(),
        "digital_footprint": footprint
    }


@app.post("/test/ollama-raw", tags=["Health Check"])
async def test_ollama_raw(file: UploadFile = File(...)):
    """
    نمایش خروجی خام مدل بدون پارس
    """
    file_bytes = await file.read()
    resume_text = PDFParserService.extract_text_from_bytes(file_bytes)

    client = AsyncNetworkService.get_client()
    payload = {
        "model": "qwen3-coder:30b",
        "prompt": f"Resume Text:\n{resume_text[:2000]}\n\nStrict JSON Output:",
        "system": OllamaAIService.SYSTEM_PROMPT,
        "stream": False,
        "format": "json"
    }
    response = await client.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=120.0
    )
    result = response.json()
    raw = result.get("response", "")
    return {
        "raw_output": raw[:1000],
        "length": len(raw)
    }
@app.post("/test/init-qdrant", tags=["Health Check"])
async def init_qdrant():
    """
    تسک ۶۴، ۶۵، ۶۶ - راه‌اندازی Qdrant و ایجاد کالکشن مهارت‌ها
    """
    result = VectorDBService.initialize_skills_collection()
    return result


@app.get("/test/qdrant-info", tags=["Health Check"])
async def qdrant_info():
    """
    دریافت اطلاعات کالکشن Qdrant
    """
    result = VectorDBService.get_collection_info()
    return result
@app.post("/test/store-embedding", tags=["Health Check"])
async def test_store_embedding():
    """
    تسک ۶۷، ۶۸، ۶۹، ۷۰ - تست کامل پایپ‌لاین امبدینگ و ذخیره در Qdrant
    """
    test_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"]
    
    result = EmbeddingService.store_candidate_skills(
        candidate_id=1,
        skills=test_skills,
        application_id=1
    )
    return {
        "status": "success",
        "result": result
    }
@app.post("/test/cosine-similarity", tags=["Health Check"])
async def test_cosine_similarity():
    """
    تسک ۷۱، ۷۲، ۷۳، ۷۴ - تست موتور شباهت کسینوسی
    """
    # تست ۱ - دو بردار مشابه
    vector_a = [1.0, 0.5, 0.3, 0.8]
    vector_b = [0.9, 0.4, 0.35, 0.75]
    similarity_high = SemanticMatchingEngine.calculate_cosine_similarity(vector_a, vector_b)

    # تست ۲ - دو بردار متفاوت
    vector_c = [1.0, 0.0, 0.0, 0.0]
    vector_d = [0.0, 1.0, 0.0, 0.0]
    similarity_low = SemanticMatchingEngine.calculate_cosine_similarity(vector_c, vector_d)

    # تست ۳ - کنترل تقسیم بر صفر
    vector_zero = [0.0, 0.0, 0.0, 0.0]
    similarity_zero = SemanticMatchingEngine.calculate_cosine_similarity(vector_a, vector_zero)

    # تست ۴ - جستجوی معنایی در Qdrant
    job_skills = ["Python", "FastAPI", "PostgreSQL"]
    matches = SemanticMatchingEngine.find_matching_candidates(job_skills)

    return {
        "status": "success",
        "tests": {
            "similar_vectors": round(similarity_high, 4),
            "different_vectors": round(similarity_low, 4),
            "zero_vector_safe": similarity_zero
        },
        "semantic_search_results": matches
    }