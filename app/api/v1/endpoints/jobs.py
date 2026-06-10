from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.crud.job import job_posting_crud
from app.models.job import JobPosting as JobPostingModel
from app.models.user import User
from app.schemas.job import JobPosting, JobPostingCreate, JobPostingUpdate

router = APIRouter()


@router.get("/", response_model=List[JobPosting])
def list_jobs(
    skip: int = 0,
    limit: int = 100,
    tier: str = None,
    keyword: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(JobPostingModel)
    if tier:
        query = query.filter(JobPostingModel.minimum_tier_required == tier)
    if keyword:
        query = query.filter(
            (JobPostingModel.job_title.ilike(f"%{keyword}%")) |
            (JobPostingModel.company_name.ilike(f"%{keyword}%"))
        )
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=JobPosting)
def create_job(
    job_in: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return job_posting_crud.create(db, obj_in=job_in)


@router.get("/{job_id}", response_model=JobPosting)
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = job_posting_crud.get(db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.put("/{job_id}", response_model=JobPosting)
def update_job(
    job_id: int,
    job_in: JobPostingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    job = job_posting_crud.get(db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job_posting_crud.update(db, db_obj=job, obj_in=job_in)


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    job = job_posting_crud.get(db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    job_posting_crud.remove(db, id=job_id)
    return {"message": "Job posting deleted"}
