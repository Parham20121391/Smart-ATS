from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.application import Application


class StateMachineService:
    """
    سرویس مدیریت وضعیت و کنترل ماتریس انتقال چرخه استخدام کاندیداها
    """

    VALID_TRANSITIONS = {
        "REGISTERED": ["PENDING_VERIFICATION"],
        "PENDING_VERIFICATION": ["SCREENING", "FLAGGED_REJECTED"],
        "SCREENING": ["TECH_INTERVIEW", "REJECTED"],
        "TECH_INTERVIEW": ["HR_INTERVIEW", "REJECTED"],
        "HR_INTERVIEW": ["OFFER_EXTENDED", "REJECTED"],
        "OFFER_EXTENDED": ["HIRED", "REJECTED"],
        "HIRED": [],
        "REJECTED": [],
        "FLAGGED_REJECTED": []
    }

    @classmethod
    def validate_state_transition_v2(cls, current_state: str, next_state: str) -> None:
        """
        بررسی اصالت و مجاز بودن انتقال وضعیت بر اساس ماتریس سختگیرانه سیستم
        """
        if current_state not in cls.VALID_TRANSITIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"وضعیت '{current_state}' در سیستم تعریف نشده است."
            )

        allowed_next_states = cls.VALID_TRANSITIONS[current_state]

        if next_state not in allowed_next_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"انتقال وضعیت از '{current_state}' به '{next_state}' غیرمجاز است. "
                       f"وضعیت‌های مجاز: {allowed_next_states}"
            )

    @classmethod
    def get_allowed_transitions(cls, current_state: str) -> list:
        """
        دریافت لیست وضعیت‌های مجاز از وضعیت فعلی
        """
        return cls.VALID_TRANSITIONS.get(current_state, [])

    @classmethod
    def enforce_state_machine_matrix(
        cls,
        application_id: int,
        next_state: str,
        db: Session
    ) -> Application:
        """
        دکوراتور اصلی - قفل‌گذاری بدبینانه و اعتبارسنجی کامل انتقال وضعیت
        """
        # قفل‌گذاری بدبینانه - جلوگیری از Race Condition
        app_record = db.query(Application).filter(
            Application.id == application_id
        ).with_for_update().first()

        if not app_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="درخواست مورد نظر یافت نشد."
            )

        # بررسی مجاز بودن انتقال در ماتریس
        cls.validate_state_transition_v2(app_record.current_status, next_state)

        # بررسی شرط امنیتی integrity_flag برای ورود به SCREENING
        if next_state == "SCREENING" and not app_record.integrity_flag:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="عبور به مرحله غربالگری به دلیل فعال بودن پرچم تخلف و "
                       "نمره اصالت پایین مجاز نیست."
            )

        # اعمال تغییر وضعیت
        app_record.current_status = next_state
        db.commit()
        db.refresh(app_record)

        return app_record