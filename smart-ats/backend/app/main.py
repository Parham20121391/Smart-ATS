import os
import asyncio
import logging
import redis
from fastapi import FastAPI, UploadFile, File, Query, Depends, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.linkedin_matching import LinkedInCrossMatchingEngine
from app.services.semantic_matching import SemanticMatchingEngine
from app.services.crawler import WebCrawlerService
from app.services.embedding_service import EmbeddingService
from app.services.network import AsyncNetworkService, OLLAMA_BASE_URL, OLLAMA_MODEL
from app.services.vector_db import VectorDBService
from app.services.pdf_parser import PDFParserService
from app.services.ai_service import OllamaAIService, ExtractedResumeSchema
from app.services.elk_logger import setup_centralized_logging
from app.services.kpi_tracker import KPITrackingService
from app.routers import jobs, applications
from app.middleware import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
    require_api_key,
    RateLimiterMiddleware
)

# تسک SAP-77: راه‌اندازی لاگینگ متمرکز FastAPI به سمت Logstash
setup_centralized_logging(service_name="smart-ats-fastapi")
logger = logging.getLogger("smart-ats-fastapi")


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Smart ATS v3.0.0 FastAPI server starting up with centralized ELK & KPI tracking.")
    AsyncNetworkService.get_client()
    yield
    await AsyncNetworkService.close_client()


app = FastAPI(
    title="Smart ATS API",
    description="سیستم هوشمند فرامرزی تجمیع‌کننده و راستی‌آزمایی جذب و استخدام (نسخه تجاری ۳.۰۰)",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(RateLimiterMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(jobs.router, dependencies=[Depends(require_api_key)])
app.include_router(applications.router, dependencies=[Depends(require_api_key)])


@app.middleware("http")
async def protect_test_routes(request: Request, call_next):
    if request.url.path.startswith("/test/"):
        try:
            require_api_key(request.headers.get("x-api-key"))
        except StarletteHTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"error": True, "message": exc.detail})
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled API error on {request.method} {request.url.path}: {exc}", exc_info=True)
        raise


@app.get("/", tags=["Health Check"])
async def root():
    loop = asyncio.get_event_loop()
    return {
        "status": "online",
        "system": "Smart ATS",
        "version": "3.0.0",
        "async_support": True,
        "event_loop_running": loop.is_running()
    }


@app.get("/health", tags=["Health Check"])
async def health_check():
    client = AsyncNetworkService.get_client()
    return {
        "status": "healthy",
        "version": "3.0.0",
        "http_client": "ready",
        "client_closed": client.is_closed
    }


@app.get("/api/v1/kpis", tags=["Commercial KPIs"], dependencies=[Depends(require_api_key)])
async def get_commercial_kpis(db: Session = Depends(get_db_session)):
    """
    تسک SAP-86, SAP-88, SAP-89, SAP-90: گزارش زنده شاخص‌های کلیدی عملکرد پلتفرم
    """
    return KPITrackingService.get_all_commercial_kpis(db)


@app.get("/metrics", tags=["Monitoring"])
async def prometheus_metrics(db: Session = Depends(get_db_session)):
    """
    تسک SAP-79, SAP-81, SAP-86..90: خروجی متریک‌های Prometheus شامل صف Celery و KPIهای تجاری
    """
    queue_len = 0
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_connect_timeout=1.5)
        queue_len = r.llen("celery")
    except Exception:
        queue_len = 0

    kpi_report = KPITrackingService.get_all_commercial_kpis(db)["kpis"]
    false_red = kpi_report["false_interview_reduction"]["current_rate_percent"]
    crawler_rate = kpi_report["crawler_success_rate"]["current_rate_percent"]
    avg_hire_hours = kpi_report["average_time_to_hire"]["average_hours"]

    metrics_text = (
        "# HELP smart_ats_celery_queue_length Number of pending tasks in Celery queue\n"
        "# TYPE smart_ats_celery_queue_length gauge\n"
        f"smart_ats_celery_queue_length {queue_len}\n"
        "# HELP smart_ats_false_interview_reduction_rate Percentage of false interviews prevented (Target >= 40%)\n"
        "# TYPE smart_ats_false_interview_reduction_rate gauge\n"
        f"smart_ats_false_interview_reduction_rate {false_red}\n"
        "# HELP smart_ats_crawler_success_rate Crawler firewall bypass success rate percentage (Target > 85%)\n"
        "# TYPE smart_ats_crawler_success_rate gauge\n"
        f"smart_ats_crawler_success_rate {crawler_rate}\n"
        "# HELP smart_ats_avg_time_to_hire_hours Average hours from PENDING_VERIFICATION to HIRED\n"
        "# TYPE smart_ats_avg_time_to_hire_hours gauge\n"
        f"smart_ats_avg_time_to_hire_hours {avg_hire_hours}\n"
    )
    return PlainTextResponse(content=metrics_text, media_type="text/plain; version=0.0.4")


@app.post("/test/ollama", tags=["Health Check"])
async def test_ollama(prompt: str = "سلام، آیا آفلاین کار می‌کنی؟"):
    """
    تست ارتباط با موتور Ollama و مدل محلی qwen3-coder
    """
    response = await AsyncNetworkService.call_ollama(prompt)
    return {
        "status": "success",
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "response": response
    }


@app.post("/test/pdf-parser", tags=["Health Check"])
async def test_pdf_parser(file: UploadFile = File(...)):
    """
    تست استخراج متن از فایل PDF رزومه
    """
    file_bytes = await file.read()
    PDFParserService.validate_pdf_bytes(file_bytes)
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
    PDFParserService.validate_pdf_bytes(file_bytes)
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
    PDFParserService.validate_pdf_bytes(file_bytes)
    resume_text = PDFParserService.extract_text_from_bytes(file_bytes)

    client = AsyncNetworkService.get_client()
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Resume Text:\n{resume_text[:2000]}\n\nStrict JSON Output:",
        "system": OllamaAIService.SYSTEM_PROMPT,
        "stream": False,
        "format": "json"
    }
    response = await client.post(
        f"{OLLAMA_BASE_URL}/api/generate",
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
    vector_a = [1.0, 0.5, 0.3, 0.8]
    vector_b = [0.9, 0.4, 0.35, 0.75]
    similarity_high = SemanticMatchingEngine.calculate_cosine_similarity(vector_a, vector_b)

    vector_c = [1.0, 0.0, 0.0, 0.0]
    vector_d = [0.0, 1.0, 0.0, 0.0]
    similarity_low = SemanticMatchingEngine.calculate_cosine_similarity(vector_c, vector_d)

    vector_zero = [0.0, 0.0, 0.0, 0.0]
    similarity_zero = SemanticMatchingEngine.calculate_cosine_similarity(vector_a, vector_zero)

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


@app.post("/test/github-verify", tags=["Health Check"])
async def test_github_verify(claimed_skill: str = Query(default="smart", description="مهارت ادعا شده")):
    """
    تسک ۸۳، ۸۴، ۸۵، ۸۶، ۸۷ - تست ورکر تحلیل عمیق GitHub
    """
    from app.celery_app import verify_github_integrity_deep

    task = verify_github_integrity_deep.delay(
        application_id=2,
        github_username="Parham20121391",
        claimed_skill=claimed_skill
    )

    return {
        "status": "queued",
        "task_id": task.id,
        "claimed_skill": claimed_skill,
        "message": "تسک تحلیل عمیق GitHub در صف Celery قرار گرفت"
    }


@app.post("/test/linkedin-match", tags=["Health Check"])
async def test_linkedin_match():
    """
    تسک ۸۸، ۸۹، ۹۰، ۹۱ - تست موتور تطابق لینکدین
    """
    resume_exp = [
        {"company": "Nextron", "months": 12, "role": "Backend Developer"},
        {"company": "Fake Company", "months": 6, "role": "Senior Dev"}
    ]

    linkedin_exp = [
        {"company": "Nextron", "months": 14},
        {"company": "Google", "months": 24}
    ]

    result = LinkedInCrossMatchingEngine.analyze_timeline_consistency(
        resume_exp=resume_exp,
        linkedin_exp=linkedin_exp
    )

    return {
        "status": "success",
        "result": result
    }


@app.post("/test/crawl", tags=["Health Check"])
async def test_crawl(url: str = Query(default="https://jobinja.ir", description="آدرس سایت هدف")):
    """
    تسک ۹۷، ۹۸، ۹۹، ۱۰۰، ۱۰۱ - تست خزنده وب با Playwright
    """
    content = await WebCrawlerService.crawl_job_page(url)
    return {
        "status": "success",
        "url": url,
        "content_length": len(content),
        "preview": content[:500]
    }