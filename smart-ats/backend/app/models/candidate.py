from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    github_username = Column(String(100))
    linkedin_profile_url = Column(String(2048))
    resume_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
