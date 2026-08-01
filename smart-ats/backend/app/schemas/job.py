from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    skills_required: Optional[List[str]] = []
    status: str
    source_type: str
    original_url: Optional[str] = None
    company_id: int
    created_at: datetime

    model_config = {"from_attributes": True}