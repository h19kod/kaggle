from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Numeric, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class CompetitionStatus(PyEnum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    COMPLETED = "Completed"


class SubmissionStatus(PyEnum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description_markdown = Column(Text, nullable=True)
    evaluation_metric = Column(String(100), nullable=True)
    ground_truth_file_path = Column(String(500), nullable=True)
    prize_pool = Column(Numeric(12, 2), default=0.00)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(CompetitionStatus), default=CompetitionStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    submissions = relationship("Submission", back_populates="competition")
    leaderboard = relationship("Leaderboard", back_populates="competition")


class Submission(Base):
    __tablename__ = "competition_submissions"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_file_url = Column(String(500), nullable=False)
    score = Column(Float, nullable=True)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    competition = relationship("Competition", back_populates="submissions")
    submitter = relationship("User", back_populates="submissions")


class Leaderboard(Base):
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    best_score = Column(Float, nullable=True)
    rank_position = Column(Integer, nullable=True)
    last_submission_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    competition = relationship("Competition", back_populates="leaderboard")
