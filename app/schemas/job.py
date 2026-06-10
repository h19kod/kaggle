from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class JobPostingBase(BaseModel):
    company_name: str
    job_title: str
    description: str
    minimum_tier_required: Optional[str] = "Novice"


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    description: Optional[str] = None
    minimum_tier_required: Optional[str] = None


class JobPosting(JobPostingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    posted_at: datetime
