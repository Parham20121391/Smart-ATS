from sentence_transformers import SentenceTransformer
from qdrant_client.http import models
from app.services.vector_db import VectorDBService, COLLECTION_NAME
import logging
import uuid

logger = logging.getLogger(__name__)

# تسک ۶۸ - انتخاب و راه‌اندازی مدل امبدینگ محلی
MODEL_NAME = "all-MiniLM-L6-v2"  # مدل سبک با خروجی ۳۸۴ بُعد - تغییر VECTOR_SIZE به ۳۸۴


class EmbeddingService:
    """
    سرویس تبدیل متون به بردارهای معنایی با مدل امبدینگ محلی
    """

    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            cls._model = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        return cls._model

    @classmethod
    def generate_embedding(cls, text: str) -> list:
        """
        تسک ۶۹ - تبدیل متن خام به بردار متراکم فضایی
        """
        model = cls.get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    @classmethod
    def store_candidate_skills(
        cls,
        candidate_id: int,
        skills: list,
        application_id: int = 0
    ) -> dict:
        """
        تسک ۷۰ - ثبت بردار مهارت‌ها با متادیتا در Qdrant
        """
        client = VectorDBService.get_client()

        # تبدیل لیست مهارت‌ها به متن یکپارچه
        skills_text = ", ".join(skills)

        # تولید بردار امبدینگ
        embedding = cls.generate_embedding(skills_text)

        # تسک ۷۰ - ثبت متادیتا (Payload) شامل candidate_id
        point_id = str(uuid.uuid4())
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "candidate_id": candidate_id,
                        "application_id": application_id,
                        "skills": skills,
                        "skills_text": skills_text
                    }
                )
            ]
        )

        logger.info(f"Skills vector stored for candidate_id: {candidate_id}")
        return {
            "point_id": point_id,
            "candidate_id": candidate_id,
            "skills_count": len(skills),
            "vector_dimensions": len(embedding)
        }