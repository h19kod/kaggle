from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.competition import Competition, Submission, Leaderboard
from app.schemas.competition import CompetitionCreate, CompetitionUpdate, SubmissionCreate, LeaderboardUpdate


class CRUDCompetition(CRUDBase[Competition, CompetitionCreate, CompetitionUpdate]):
    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Competition]:
        return (
            db.query(Competition)
            .filter(Competition.status == "Active")
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDSubmission(CRUDBase[Submission, SubmissionCreate, SubmissionCreate]):
    def get_by_competition(self, db: Session, *, competition_id: int, skip: int = 0, limit: int = 100) -> List[Submission]:
        return (
            db.query(Submission)
            .filter(Submission.competition_id == competition_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Submission]:
        return (
            db.query(Submission)
            .filter(Submission.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDLeaderboard(CRUDBase[Leaderboard, LeaderboardUpdate, LeaderboardUpdate]):
    def get_by_competition(self, db: Session, *, competition_id: int) -> List[Leaderboard]:
        return (
            db.query(Leaderboard)
            .filter(Leaderboard.competition_id == competition_id)
            .order_by(Leaderboard.rank_position.asc())
            .all()
        )

    def get_by_user_and_competition(self, db: Session, *, user_id: int, competition_id: int) -> Optional[Leaderboard]:
        return (
            db.query(Leaderboard)
            .filter(Leaderboard.user_id == user_id, Leaderboard.competition_id == competition_id)
            .first()
        )

    def recalculate_ranks(self, db: Session, *, competition_id: int) -> None:
        entries = (
            db.query(Leaderboard)
            .filter(Leaderboard.competition_id == competition_id)
            .order_by(Leaderboard.best_score.desc())
            .all()
        )
        for idx, entry in enumerate(entries, start=1):
            entry.rank_position = idx
        db.commit()


competition_crud = CRUDCompetition(Competition)
submission_crud = CRUDSubmission(Submission)
leaderboard_crud = CRUDLeaderboard(Leaderboard)
