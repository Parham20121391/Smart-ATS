# smart-ats/backend/app/routers/applications.py
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.schemas.application import ApplicationCreateResponse, VerificationResponse
from app.services.state_machine import StateMachineService
from app.database import get_db
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.pdf_parser import PDFParserService
from app.services.websocket_manager import ws_manager
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/api/v1", tags=["Applications"])


# تسک ۳۹: راه‌‌اندازی اندپوینت اختصاصی وب‌سوکت
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
    db: Session = Depends(get_db)
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
async def get_application_verification(id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درخواست مورد نظر یافت نشد.")
    return application


@router.post("/applications/transition", status_code=status.HTTP_200_OK, tags=["State Machine"])
async def test_state_transition(
    current_state: str = Query(..., description="وضعیت فعلی کاندیدا"),
    next_state: str = Query(..., description="وضعیت جدید درخواستی")
):
    StateMachineService.validate_state_transition_v2(current_state, next_state)
    allowed = StateMachineService.get_allowed_transitions(current_state)
    return {
        "current_state": current_state,
        "next_state": next_state,
        "transition_valid": True,
        "allowed_transitions": allowed
    }


# تسک ۴۰: به‌روزرسانی وضعیت و مخابره رویداد به وب‌سوکت
@router.patch("/applications/{application_id}/status", status_code=status.HTTP_200_OK, tags=["State Machine"])
async def update_application_status(
    application_id: int,
    next_state: str = Query(..., description="وضعیت جدید درخواستی"),
    db: Session = Depends(get_db)
):
    updated_app = StateMachineService.enforce_state_machine_matrix(
        application_id=application_id,
        next_state=next_state,
        db=db
    )

    # مخابره تغییر وضعیت به کلاینت‌های متصل
    await ws_manager.broadcast_candidate_update(
        candidate_id=updated_app.id,
        next_state=updated_app.current_status
    )

    return {
        "application_id": updated_app.id,
        "current_status": updated_app.current_status,
        "integrity_flag": updated_app.integrity_flag
    }