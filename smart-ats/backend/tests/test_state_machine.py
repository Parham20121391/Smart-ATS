import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.services.state_machine import StateMachineService

def test_valid_state_transitions():
    """تست انتقال‌های معتبر طبق ماتریس ماشین وضعیت"""
    StateMachineService.validate_state_transition_v2("REGISTERED", "PENDING_VERIFICATION")
    StateMachineService.validate_state_transition_v2("PENDING_VERIFICATION", "SCREENING")
    StateMachineService.validate_state_transition_v2("PENDING_VERIFICATION", "FLAGGED_REJECTED")
    StateMachineService.validate_state_transition_v2("SCREENING", "TECH_INTERVIEW")
    StateMachineService.validate_state_transition_v2("TECH_INTERVIEW", "HR_INTERVIEW")
    StateMachineService.validate_state_transition_v2("HR_INTERVIEW", "OFFER_EXTENDED")
    StateMachineService.validate_state_transition_v2("OFFER_EXTENDED", "HIRED")

def test_invalid_state_transitions():
    """تست پرش غیرمجاز بین وضعیت‌ها (پرتاب خطای ۴۰۰)"""
    with pytest.raises(HTTPException) as exc_info:
        StateMachineService.validate_state_transition_v2("REGISTERED", "HIRED")
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        StateMachineService.validate_state_transition_v2("HIRED", "SCREENING")
    assert exc_info.value.status_code == 400

def test_enforce_state_machine_matrix_integrity_flag_pass():
    """تست ماک شده تایید عبور به مرحله غربالگری با داشتن اصالت سنجی معتبر"""
    mock_db = MagicMock()
    mock_app = MagicMock()
    mock_app.id = 1
    mock_app.current_status = "PENDING_VERIFICATION"
    mock_app.integrity_flag = True

    # پشتیبانی از هر دو حالت کوئری معمولی و کوئری دارای with_for_update
    mock_db.query.return_value.filter.return_value.first.return_value = mock_app
    mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_app

    updated_app = StateMachineService.enforce_state_machine_matrix(
        application_id=1,
        next_state="SCREENING",
        db=mock_db
    )
    assert updated_app.current_status == "SCREENING"
    assert mock_db.commit.called

def test_enforce_state_machine_matrix_integrity_flag_fail():
    """تست ماک شده رد عبور به مرحله غربالگری به علت فقدان اصالت سنجی (پرتاب خطای ۴۰۳)"""
    mock_db = MagicMock()
    mock_app = MagicMock()
    mock_app.id = 2
    mock_app.current_status = "PENDING_VERIFICATION"
    mock_app.integrity_flag = False

    # پشتیبانی از هر دو حالت کوئری معمولی و کوئری دارای with_for_update
    mock_db.query.return_value.filter.return_value.first.return_value = mock_app
    mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_app

    with pytest.raises(HTTPException) as exc_info:
        StateMachineService.enforce_state_machine_matrix(
            application_id=2,
            next_state="SCREENING",
            db=mock_db
        )
    assert exc_info.value.status_code == 403