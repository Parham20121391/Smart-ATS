from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, func
from sqlalchemy.dialects.postgresql import ENUM
from app.database import Base

application_status_enum = ENUM(
    'REGISTERED',
    'PENDING_VERIFICATION',
    'SCREENING',
    'TECH_INTERVIEW',
    'HR_INTERVIEW',
    'OFFER_EXTENDED',
    'HIRED',
    'REJECTED',
    'FLAGGED_REJECTED',
    name='application_status_enum',
    create_type=False  # چون قبلاً توی migration ساختیم
)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, nullable=False)
    candidate_id = Column(Integer, nullable=False)
    current_status = Column(application_status_enum, default='REGISTERED', nullable=False)
    score = Column(Float, default=0.0)
    github_verification_score = Column(Float, default=0.0)
    linkedin_match_status = Column(String(100), default='UNVERIFIED')
    integrity_flag = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)