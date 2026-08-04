from fastapi import HTTPException, status


class StateMachineService:
    """
    سرویس مدیریت وضعیت و کنترل ماتریس انتقال چرخه استخدام کاندیداها
    """

    # تعریف دقیق مقاصد مجاز از هر مبدا وضعیت
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
        بررسی اصالت و مجاز بودن انتقال وضعیت بر اساس ماتریس سختگیرانه سیستم.
        در صورت غیرمجاز بودن، خطای ۴۰۰ صادر می‌شود.
        """
        # بررسی وجود وضعیت فعلی در ماتریس
        if current_state not in cls.VALID_TRANSITIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"وضعیت '{current_state}' در سیستم تعریف نشده است."
            )

        allowed_next_states = cls.VALID_TRANSITIONS[current_state]

        # بررسی مجاز بودن انتقال به وضعیت جدید
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