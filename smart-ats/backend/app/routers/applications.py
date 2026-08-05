from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.application import ApplicationCreateResponse, VerificationResponse
from app.services.state_machine import StateMachineService
from app.database import get_db

router = APIRouter(prefix="/api/v1", tags=["Applications"])


@router.post("/applications", response_model=ApplicationCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_application(
    job_id: int = Query(..., description="شناسه آگهی شغلی"),
    github_username: str = Query(..., description="شناسه گیت‌هاب کارجو"),
    linkedin_url: str = Query(..., description="آدرس پروفایل لینکدین کارجو"),
    file: UploadFile = File(..., description="فایل رزومه PDF")
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="پایپلاین پردازش رزومه در فاز بعدی پیاده‌سازی می‌شود."
    )


@router.get("/applications/verification/{id}", response_model=VerificationResponse, status_code=status.HTTP_200_OK)
async def get_application_verification(id: int):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="این اندپوینت در فاز بعدی به لایه راستی‌آزمایی متصل می‌شود."
    )


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
    return {
        "application_id": updated_app.id,
        "current_status": updated_app.current_status,
        "integrity_flag": updated_app.integrity_flag
    }