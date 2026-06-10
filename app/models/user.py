from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class UserTier(PyEnum):
    NOVICE = "Novice"
    CONTRIBUTOR = "Contributor"
    EXPERT = "Expert"
    MASTER = "Master"
    GRANDMASTER = "Grandmaster"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    global_tier = Column(Enum(UserTier), default=UserTier.NOVICE)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    datasets = relationship("Dataset", back_populates="owner")
    notebooks = relationship("Notebook", back_populates="creator")
    submissions = relationship("Submission", back_populates="submitter")
    progress = relationship("UserCourseProgress", back_populates="user")
    posts = relationship("DiscussionPost", back_populates="author")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    github_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    is_seeking_job = Column(Boolean, default=False)
    total_upvotes = Column(Integer, default=0)

    user = relationship("User", back_populates="profile")
