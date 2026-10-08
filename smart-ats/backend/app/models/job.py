from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from app.database import Base


job_source_enum = ENUM(
    'INTERNAL', 'LINKEDIN', 'GOOGLE', 'JOBINJA', 'QUERA',
    name='job_source_enum', create_type=False
)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    skills_required = Column(ARRAY(String(100)))
    status = Column(String(50), default="ACTIVE", nullable=False)
    source_type = Column(job_source_enum, default="INTERNAL", nullable=False)
    original_url = Column(String(2048))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
