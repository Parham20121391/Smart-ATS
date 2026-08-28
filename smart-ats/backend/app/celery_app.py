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
def verify_github_integrity_deep(application_id: int, github_username: str, claimed_skill: str = "python"):
    """
    تسک ۸۳ - تحلیل عمیق مخازن گیت‌هاب و تولید نمره اصالت
    """
    if not github_username:
        return "NO_GITHUB_PROVIDED"

    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    api_url = f"https://api.github.com/users/{github_username}/repos"

    with httpx.Client(timeout=15.0) as client:
        response = client.get(api_url, headers=headers)

        if response.status_code == 404:
            logger.warning(f"GitHub user not found: {github_username}")
            return "INVALID_GITHUB_ACCOUNT"

        if response.status_code != 200:
            raise httpx.HTTPError(f"GitHub API returned {response.status_code}")

        repos = response.json()

        match_count = 0
        total_stars = 0
        has_dependency = False

        for repo in repos:
            repo_name = repo.get("name", "").lower()
            description = (repo.get("description") or "").lower()

            # تسک ۸۴ - جستجوی تطابقی در name و description
            if claimed_skill.lower() in repo_name or claimed_skill.lower() in description:
                match_count += 1
                total_stars += repo.get("stargazers_count", 0)

                # تسک ۸۵ - اسکن فایل‌های پیکربندی
                contents_url = f"https://api.github.com/repos/{github_username}/{repo.get('name')}/contents"
                contents_resp = client.get(contents_url, headers=headers)

                if contents_resp.status_code == 200:
                    files = [f.get("name") for f in contents_resp.json() if isinstance(f, dict)]
                    if "requirements.txt" in files or "pyproject.toml" in files or "package.json" in files:
                        has_dependency = True

        # تسک ۸۶ - فرمول وزن‌دار نمره اصالت
        base_score = min((match_count / 2) * 60, 60)
        dependency_bonus = 25 if has_dependency else 0
        popularity_bonus = min(total_stars * 3, 15)
        final_score = float(base_score + dependency_bonus + popularity_bonus)

        logger.info(f"GitHub score for {github_username}: {final_score}")

        # تسک ۸۷ - ذخیره نمره در دیتابیس با اصول ACID
        try:
            from sqlalchemy import create_engine, text
            from dotenv import load_dotenv
            load_dotenv()
            
            engine = create_engine(os.getenv("DATABASE_URL"))
            
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE applications 
                        SET github_verification_score = :score,
                            integrity_flag = :flag
                        WHERE id = :app_id
                    """),
                    {
                        "score": final_score,
                        "flag": final_score >= 50,
                        "app_id": application_id
                    }
                )
            logger.info(f"DB updated for application_id: {application_id}")
        except Exception as e:
            logger.error(f"DB update failed: {str(e)}")

        return {
            "application_id": application_id,
            "github_username": github_username,
            "claimed_skill": claimed_skill,
            "repos_count": len(repos),
            "match_count": match_count,
            "has_dependency": has_dependency,
            "final_score": final_score,
            "integrity_flag": final_score >= 50,
            "status": "SUCCESS"
        }


@celery_app.task(name="tasks.verify_linkedin")
def verify_linkedin(application_id: int, linkedin_url: str):
    logger.info(f"LinkedIn verification started for: {linkedin_url}")
    return {
        "application_id": application_id,
        "linkedin_url": linkedin_url,
        "status": "queued"
    }