# smart-ats/backend/app/routers/applications.py
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.schemas.application import ApplicationCreateResponse, VerificationResponse
from app.services.state_machine import StateMachineService
from app.database import get_db
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.pdf_parser import PDFParserService
from app.services.websocket_manager import ws_manager
from app.services.auth import (
    get_current_user_role,
    RoleChecker,
    require_admin,
    require_hr_or_admin,
    require_tech_or_admin
)
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/api/v1", tags=["Applications"])


@router.websocket("/ws/kanban")
async def websocket_kanban_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


@router.post("/applications", response_model=ApplicationCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_application(
    job_id: int = Query(..., description="شناسه آگهی شغلی"),
    candidate_id: int = Query(..., description="شناسه کارجو"),
    github_username: str = Query(..., description="شناسه گیت‌هاب کارجو"),
    linkedin_url: str = Query(..., description="آدرس پروفایل لینکدین کارجو"),
    file: UploadFile = File(..., description="فایل رزومه PDF"),
    db: Session = Depends(get_db),
    # تسک ۵۰ و ۵۳: کارجو یا ادمین/HR می‌توانند رزومه ارسال کنند
    current_user: Dict[str, Any] = Depends(RoleChecker(["Admin", "HR Manager", "Candidate"]))
):
    file_bytes = await file.read()
    PDFParserService.validate_pdf_bytes(file_bytes)
    if not db.query(Job.id).filter(Job.id == job_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="آگهی شغلی یافت نشد.")
    if not db.query(Candidate.id).filter(Candidate.id == candidate_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="کارجو یافت نشد.")
    
    application = Application(job_id=job_id, candidate_id=candidate_id, current_status="PENDING_VERIFICATION")
    db.add(application)
    try:
        db.commit()
        db.refresh(application)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="این کارجو قبلاً برای آگهی درخواست ثبت کرده است.")
    
    from app.celery_app import verify_github_integrity_deep, verify_linkedin
    if github_username:
        verify_github_integrity_deep.delay(application.id, github_username)
    if linkedin_url:
        verify_linkedin.delay(application.id, linkedin_url)
    return application


@router.get("/applications/verification/{id}", response_model=VerificationResponse, status_code=status.HTTP_200_OK)
async def get_application_verification(
    id: int,
    db: Session = Depends(get_db),
    # تسک ۵۲، ۵۳، ۵۴: فقط HR، Tech Lead و Admin دسترسی مشاهده نتایج راستی‌آزمایی را دارند
    current_user: Dict[str, Any] = Depends(RoleChecker(["Admin", "HR Manager", "Tech Lead"]))
):
    application = db.query(Application).filter(Application.id == id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درخواست مورد نظر یافت نشد.")
    
    # تسک ۵۴: تک‌لید فقط در وضعیت مصاحبه فنی مجاز به دیدن اطلاعات متقاضی است
    if current_user["role"] == "Tech Lead" and application.current_status != "TECH_INTERVIEW":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="مدیر فنی صرفاً به کاندیداهای مرحله TECH_INTERVIEW دسترسی دارد."
        )

    return application


@router.patch("/applications/{application_id}/status", status_code=status.HTTP_200_OK, tags=["State Machine"])
async def update_application_status(
    application_id: int,
    next_state: str = Query(..., description="وضعیت جدید درخواستی"),
    db: Session = Depends(get_db),
    # تسک ۵۰ و ۵۵: احراز هویت نقش‌های سازمانی
    current_user: Dict[str, Any] = Depends(RoleChecker(["Admin", "HR Manager", "Tech Lead"]))
):
    user_role = current_user["role"]
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درخواست مورد نظر یافت نشد.")

    # تسک ۵۴: Tech Lead تنها مجاز به تغییر وضعیت از مرحله TECH_INTERVIEW است
    if user_role == "Tech Lead" and app_record.current_status != "TECH_INTERVIEW":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز: مدیر فنی صرفاً مجاز به ثبت ارزیابی کاندیداهای مستقر در وضعیت TECH_INTERVIEW است."
        )

    # تسک ۵۳: محدودیت HR برای مداخله در ارزیابی فنی مستقیم
    if user_role == "HR Manager" and app_record.current_status == "TECH_INTERVIEW" and next_state != "REJECTED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="تغییر وضعیت کاندیدا در مرحله مصاحبه فنی صرفاً توسط Tech Lead انجام می‌پذیرد."
        )

    updated_app = StateMachineService.enforce_state_machine_matrix(
        application_id=application_id,
        next_state=next_state,
        db=db
    )

    await ws_manager.broadcast_candidate_update(
        candidate_id=updated_app.id,
        next_state=updated_app.current_status
    )

    return {
        "application_id": updated_app.id,
        "current_status": updated_app.current_status,
        "integrity_flag": updated_app.integrity_flag
    }