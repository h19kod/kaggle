from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CompetitionBase(BaseModel):
    title: str
    description_markdown: Optional[str] = None
    evaluation_metric: Optional[str] = None
    ground_truth_file_path: Optional[str] = None
    prize_pool: Optional[Decimal] = Decimal("0.00")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CompetitionCreate(CompetitionBase):
    creator_id: int


class CompetitionUpdate(BaseModel):
    title: Optional[str] = None
    description_markdown: Optional[str] = None
    evaluation_metric: Optional[str] = None
    ground_truth_file_path: Optional[str] = None
    prize_pool: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None


class Competition(CompetitionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    creator_id: int
    status: str
    created_at: datetime


class SubmissionBase(BaseModel):
    competition_id: int
    submitted_file_url: str


class SubmissionCreate(SubmissionBase):
    user_id: int


class Submission(SubmissionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    score: Optional[float] = None
    status: str
    submitted_at: datetime


class LeaderboardBase(BaseModel):
    competition_id: int
    user_id: int


class LeaderboardUpdate(BaseModel):
    best_score: Optional[float] = None
    rank_position: Optional[int] = None


class Leaderboard(LeaderboardBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    best_score: Optional[float] = None
    rank_position: Optional[int] = None
    last_submission_time: datetime
