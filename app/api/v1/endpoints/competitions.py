from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.redis_client import cache
from app.crud.competition import competition_crud, submission_crud, leaderboard_crud
from app.models.competition import Competition as CompetitionModel
from app.models.user import User
from app.schemas.competition import Competition, CompetitionCreate, CompetitionUpdate, Submission, SubmissionCreate, Leaderboard

router = APIRouter()


@router.get("/", response_model=List[Competition])
def list_competitions(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
):
    if status:
        return (
            db.query(CompetitionModel)
            .filter(CompetitionModel.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )
    return competition_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=Competition)
def create_competition(
    competition_in: CompetitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition_in.creator_id = current_user.id
    return competition_crud.create(db, obj_in=competition_in)


@router.get("/{competition_id}", response_model=Competition)
def read_competition(competition_id: int, db: Session = Depends(get_db)):
    competition = competition_crud.get(db, id=competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition


@router.put("/{competition_id}", response_model=Competition)
def update_competition(
    competition_id: int,
    competition_in: CompetitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = competition_crud.get(db, id=competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    if competition.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return competition_crud.update(db, db_obj=competition, obj_in=competition_in)


@router.delete("/{competition_id}")
def delete_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = competition_crud.get(db, id=competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    if competition.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    competition_crud.remove(db, id=competition_id)
    return {"message": "Competition deleted"}


@router.get("/{competition_id}/submissions", response_model=List[Submission])
def list_submissions(competition_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return submission_crud.get_by_competition(db, competition_id=competition_id, skip=skip, limit=limit)


@router.post("/{competition_id}/submissions", response_model=Submission)
def create_submission(
    competition_id: int,
    submission_in: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = competition_crud.get(db, id=competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    if competition.end_date:
        now = datetime.now(timezone.utc)
        end_date = competition.end_date
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        if now > end_date:
            raise HTTPException(status_code=400, detail="Competition deadline has passed")
    submission_in.competition_id = competition_id
    submission_in.user_id = current_user.id
    submission = submission_crud.create(db, obj_in=submission_in)
    from app.tasks.evaluation import evaluate_submission
    evaluate_submission.delay(submission.id, competition_id)
    return submission


@router.get("/{competition_id}/leaderboard")
def get_leaderboard(competition_id: int, db: Session = Depends(get_db)):
    cached = cache.get_leaderboard(competition_id)
    if cached:
        return {"source": "cache", "data": cached}
    data = leaderboard_crud.get_by_competition(db, competition_id=competition_id)
    return {"source": "database", "data": data}
