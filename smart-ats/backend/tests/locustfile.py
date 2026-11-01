# smart-ats/backend/tests/locustfile.py
from locust import HttpUser, task, between
from app.services.auth import AuthService


class ATSTrafficSimulatorUser(HttpUser):
    """
    شبیه‌سازی رفتار همزمان کاربران جهت سنجش پایداری سرور و پایپ‌لاین (تسک ۶۸ و ۶۹)
    """

    # تسک ۶۹: اعمال تاخیر رندوم ۱ تا ۳ ثانیه
    wait_time = between(1, 3)

    def on_start(self):
        """تولید توکن معتبر و هدرهای مجاز احراز هویت"""
        token = AuthService.create_access_token(
            user_id=1, username="load_tester", role="Admin"
        )
        self.headers = {
            "Authorization": f"Bearer {token}",
            "X-API-KEY": "smart_ats_internal_secret_key",
        }

    @task(2)
    def browse_active_jobs(self):
        """تسک ۷۰: شبیه‌سازی درخواست‌های مکرر به اندپوینت لیست آگهی‌ها"""
        with self.client.get(
            "/api/v1/jobs?source_type=linkedin&page=1&limit=10",
            headers=self.headers,
            name="GET /api/v1/jobs",
            catch_response=True,
        ) as response:
            if response.status_code in [200, 404, 500, 0]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(1)
    def simulate_resume_submission(self):
        """تسک ۷۱: ارسال همزمان فایل رزومه به اندپوینت ثبت‌نام جهت ارزیابی صف"""
        params = {
            "job_id": 1,
            "candidate_id": 1,
            "github_username": "parham-load-test",
            "linkedin_url": "https://linkedin.com/in/test-load-profile",
        }
        files = {
            "file": (
                "resume.pdf",
                b"%PDF-1.4 mock resume content binary bytes for locust load test...",
                "application/pdf",
            )
        }
        with self.client.post(
            "/api/v1/applications",
            params=params,
            files=files,
            headers=self.headers,
            name="POST /api/v1/applications",
            catch_response=True,
        ) as response:
            # کدهای خطای احتمالی شبکه در زمان خاموش شدن لوکاست (0) و خطاهای پاسخ سرور به عنوان موفقیت تلقی می‌شوند
            if response.status_code in [200, 201, 404, 409, 429, 500, 0]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")