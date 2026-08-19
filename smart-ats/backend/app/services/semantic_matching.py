import numpy as np
from app.services.vector_db import VectorDBService, COLLECTION_NAME
from app.services.embedding_service import EmbeddingService
import logging

logger = logging.getLogger(__name__)


class SemanticMatchingEngine:
    """
    موتور تطبیق معنایی کاندیداها با نیازمندی‌های شغلی
    بر اساس فرمول ریاضی شباهت کسینوسی
    """

    @staticmethod
    def calculate_cosine_similarity(vector_a: list, vector_b: list) -> float:
        """
        تسک ۷۲ - پیاده‌سازی دستی شباهت کسینوسی
        تسک ۷۳ - محاسبه ضرب داخلی و نرم‌های برداری
        تسک ۷۴ - کنترل خطای تقسیم بر صفر

        فرمول: similarity = (A · B) / (||A|| × ||B||)
        """
        arr_a = np.array(vector_a)
        arr_b = np.array(vector_b)

        # تسک ۷۳ - ضرب داخلی دو بردار
        dot_product = np.dot(arr_a, arr_b)

        # تسک ۷۳ - محاسبه نرم‌های برداری
        norm_a = np.linalg.norm(arr_a)
        norm_b = np.linalg.norm(arr_b)

        # تسک ۷۴ - کنترل تقسیم بر صفر
        if norm_a == 0 or norm_b == 0:
            logger.warning("Zero norm detected - returning similarity 0.0")
            return 0.0

        similarity = float(dot_product / (norm_a * norm_b))

        # محدود کردن بین ۰ و ۱
        return max(0.0, min(1.0, similarity))

    @classmethod
    def find_matching_candidates(
        cls,
        job_skills: list,
        top_k: int = 5,
        score_threshold: float = 0.70
    ) -> list:
        """
        جستجوی کاندیداهای مناسب بر اساس شباهت معنایی با نیازمندی‌های شغل
        """
        client = VectorDBService.get_client()

        # تبدیل مهارت‌های شغل به بردار
        job_text = ", ".join(job_skills)
        job_embedding = EmbeddingService.generate_embedding(job_text)

        # جستجو در Qdrant با API جدید
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=job_embedding,
            limit=top_k,
            score_threshold=score_threshold
        )

        matches = []
        for hit in search_result.points:
            matches.append({
                "candidate_id": hit.payload.get("candidate_id"),
                "similarity_score": round(hit.score, 4),
                "skills": hit.payload.get("skills", [])
            })

        return matches