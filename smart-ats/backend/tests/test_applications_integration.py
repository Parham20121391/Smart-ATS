import io
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.database import get_db
from app.services.auth import get_current_user_role, AuthService
from app.models.application import Application

client = TestClient(app)

# بای‌پس گاردهای احراز هویت برای ایزولاسیون محیط تست
mock_user = {"user_id": 1, "username": "admin_tester", "role": "Admin"}
app.dependency_overrides[get_current_user_role] = lambda: mock_user

def test_submit_application_pipeline_integration():
    """تست یکپارچگی ثبت رزومه، ایجاد رکورد با وضعیت PENDING_VERIFICATION و بازگشت کد ۲۰۱"""
    fake_pdf = io.BytesIO(b"%PDF-1.4 mock resume content binary bytes for testing")
    fake_pdf.name = "resume.pdf"

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(id=1)

    # شبیه‌سازی رفتار بازگشتی دیتابیس در زمان ذخیره آبجکت Application
    def fake_refresh(obj):
        if isinstance(obj, Application):
            obj.id = 1
            obj.integrity_flag = True
            obj.created_at = datetime.now(timezone.utc)

    mock_db.refresh.side_effect = fake_refresh
    app.dependency_overrides[get_db] = lambda: mock_db

    test_token = AuthService.create_access_token(user_id=1, username="admin_tester", role="Admin")
    headers = {
        "Authorization": f"Bearer {test_token}",
        "X-API-KEY": "smart_ats_internal_secret_key"
    }

    with patch("app.services.pdf_parser.PDFParserService.validate_pdf_bytes", return_value=True), \
         patch("app.celery_app.verify_github_integrity_deep.delay") as mock_github_task, \
         patch("app.celery_app.verify_linkedin.delay") as mock_linkedin_task:

        response = client.post(
            "/api/v1/applications",
            params={
                "job_id": 1,
                "candidate_id": 1,
                "github_username": "test_dev",
                "linkedin_url": "https://linkedin.com/in/test_dev"
            },
            files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["current_status"] == "PENDING_VERIFICATION"
        assert data["id"] == 1
        assert data["integrity_flag"] is True
        assert mock_db.commit.called
        assert mock_github_task.called
        assert mock_linkedin_task.called

    app.dependency_overrides.clear()