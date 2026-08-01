from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationCreateResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    current_status: str
    integrity_flag: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class VerificationResponse(BaseModel):
    id: int
    github_verification_score: float
    linkedin_match_status: str
    integrity_flag: bool
    current_status: str

    model_config = {"from_attributes": True}