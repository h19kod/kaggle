from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class JobTierRequirement(PyEnum):
    NOVICE = "Novice"
    CONTRIBUTOR = "Contributor"
    EXPERT = "Expert"
    MASTER = "Master"
    GRANDMASTER = "Grandmaster"


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    minimum_tier_required = Column(Enum(JobTierRequirement), default=JobTierRequirement.NOVICE)
    posted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
