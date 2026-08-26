from celery import Celery
from dotenv import load_dotenv
import os
import httpx
import logging

load_dotenv()

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

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


@celery_app.task(
    name="tasks.verify_github_integrity_deep",
    autoretry_for=(httpx.HTTPError, httpx.ConnectError),
    max_retries=3,
    default_retry_delay=60
)
def verify_github_integrity_deep(application_id: int, github_username: str):
    """
    تسک ۸۰ - ورکر ناهمگام با autoretry برای خطاهای HTTP
    تسک ۸۱ - کلاینت همگام با timeout و هدرهای احراز هویت
    تسک ۸۲ - دریافت لیست مخازن عمومی از GitHub API
    """
    if not github_username:
        return "NO_GITHUB_PROVIDED"

    # تسک ۸۱ - هدرهای احراز هویت
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    api_url = f"https://api.github.com/users/{github_username}/repos"

    # تسک ۸۱ - کلاینت همگام با timeout مناسب
    with httpx.Client(timeout=15.0) as client:
        response = client.get(api_url, headers=headers)

        if response.status_code == 404:
            logger.warning(f"GitHub user not found: {github_username}")
            return "INVALID_GITHUB_ACCOUNT"

        if response.status_code != 200:
            logger.error(f"GitHub API error: {response.status_code}")
            raise httpx.HTTPError(f"GitHub API returned {response.status_code}")

        # تسک ۸۲ - پردازش لیست مخازن
        repos = response.json()
        logger.info(f"Found {len(repos)} repos for {github_username}")

        return {
            "application_id": application_id,
            "github_username": github_username,
            "repos_count": len(repos),
            "status": "SUCCESS",
            "repos": [
                {
                    "name": repo.get("name"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count", 0),
                    "description": repo.get("description", "")
                }
                for repo in repos[:10]  # فقط ۱۰ مخزن اول
            ]
        }


@celery_app.task(name="tasks.verify_linkedin")
def verify_linkedin(application_id: int, linkedin_url: str):
    """
    تسک ناهمگام اعتبارسنجی پروفایل لینکدین کارجو
    """
    logger.info(f"LinkedIn verification started for: {linkedin_url}")
    return {
        "application_id": application_id,
        "linkedin_url": linkedin_url,
        "status": "queued"
    }