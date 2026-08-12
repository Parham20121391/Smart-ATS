from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "smart_ats_workers",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tehran",
    enable_utc=True,
)


@celery_app.task(name="tasks.verify_github")
def verify_github(application_id: int, github_username: str):
    """
    تسک ناهمگام اعتبارسنجی مخازن گیت‌هاب کارجو
    """
    print(f"[CELERY] GitHub verification started for: {github_username}")
    return {
        "application_id": application_id,
        "github_username": github_username,
        "status": "queued"
    }


@celery_app.task(name="tasks.verify_linkedin")
def verify_linkedin(application_id: int, linkedin_url: str):
    """
    تسک ناهمگام اعتبارسنجی پروفایل لینکدین کارجو
    """
    print(f"[CELERY] LinkedIn verification started for: {linkedin_url}")
    return {
        "application_id": application_id,
        "linkedin_url": linkedin_url,
        "status": "queued"
    }