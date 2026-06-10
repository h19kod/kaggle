from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.job import JobPosting
from app.schemas.job import JobPostingCreate, JobPostingUpdate


class CRUDJobPosting(CRUDBase[JobPosting, JobPostingCreate, JobPostingUpdate]):
    def get_by_tier(self, db: Session, *, tier: str, skip: int = 0, limit: int = 100) -> List[JobPosting]:
        return (
            db.query(JobPosting)
            .filter(JobPosting.minimum_tier_required == tier)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[JobPosting]:
        return (
            db.query(JobPosting)
            .offset(skip)
            .limit(limit)
            .all()
        )


job_posting_crud = CRUDJobPosting(JobPosting)
