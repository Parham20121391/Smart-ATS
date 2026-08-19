from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

logger = logging.getLogger(__name__)

COLLECTION_NAME = "smart_ats_skills_embeddings"
VECTOR_SIZE = 768


class VectorDBService:
    """
    سرویس مدیریت پایگاه داده برداری Qdrant
    جهت جستجوی معنایی مهارت‌ها و تطابق کاندیداها
    """

    _client: QdrantClient = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        if cls._client is None:
            cls._client = QdrantClient(host="localhost", port=6333)
            logger.info("Qdrant client initialized on localhost:6333")
        return cls._client

    @classmethod
    def initialize_skills_collection(cls) -> dict:
        """
        تسک ۶۵ - ایجاد کالکشن smart_ats_skills_embeddings
        تسک ۶۶ - پیکربندی ابعاد ۷۶۸ و متریک کسینوسی
        """
        client = cls.get_client()

        existing = [c.name for c in client.get_collections().collections]

        if COLLECTION_NAME in existing:
            logger.info(f"Collection '{COLLECTION_NAME}' already exists.")
            return {
                "status": "already_exists",
                "collection": COLLECTION_NAME
            }

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfigDiff(
                default_segment_number=2
            )
        )

        logger.info(f"Collection '{COLLECTION_NAME}' created with COSINE metric and {VECTOR_SIZE} dimensions.")
        return {
            "status": "created",
            "collection": COLLECTION_NAME,
            "vector_size": VECTOR_SIZE,
            "distance": "COSINE"
        }

    @classmethod
    def get_collection_info(cls) -> dict:
        """
        دریافت اطلاعات کالکشن برای تایید استقرار
        """
        client = cls.get_client()
        info = client.get_collection(COLLECTION_NAME)
        return {
            "name": COLLECTION_NAME,
            "status": str(info.status),
            "vector_size": info.config.params.vectors.size,
            "distance": str(info.config.params.vectors.distance)
        }