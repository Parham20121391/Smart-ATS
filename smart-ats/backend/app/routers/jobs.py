from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from app.schemas.job import JobResponse
from app.services.semantic_matching import SemanticMatchingEngine

router = APIRouter(prefix="/api/v1", tags=["Jobs"])


@router.get("/jobs", response_model=List[JobResponse], status_code=status.HTTP_200_OK)
async def get_jobs(
    source_type: Optional[str] = Query(None, description="فیلتر بر اساس منبع آگهی کراول شده"),
    page: int = Query(1, ge=1, description="شماره صفحه"),
    limit: int = Query(10, le=100, description="تعداد آیتم در هر صفحه")
):
    """
    دریافت لیست آگهی‌های شغلی با قابلیت فیلترینگ پیشرفته و صفحه‌بندی.
    """
    return []


@router.post("/jobs/match-candidates", status_code=status.HTTP_200_OK, tags=["Semantic Search"])
async def match_candidates_to_job(
    skills: List[str] = Query(..., description="لیست مهارت‌های مورد نیاز شغل"),
    score_threshold: float = Query(0.70, ge=0.0, le=1.0, description="حد نصاب شباهت"),
    top_k: int = Query(5, ge=1, le=20, description="تعداد نتایج")
):
    """
    تسک ۷۵، ۷۶، ۷۷، ۷۸ - جستجوی کاندیداهای منطبق بر اساس مهارت‌های شغل
    فیلتر خودکار نتایج نامرتبط با score_threshold
    """
    matches = SemanticMatchingEngine.find_matching_candidates(
        job_skills=skills,
        top_k=top_k,
        score_threshold=score_threshold
    )
    return {
        "status": "success",
        "score_threshold": score_threshold,
        "total_matches": len(matches),
        "candidates": matches
    }