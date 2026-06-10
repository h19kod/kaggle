from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class DifficultyLevel(PyEnum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    lessons = relationship("Lesson", back_populates="course", order_by="Lesson.order_index")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    text_content = Column(Text, nullable=True)
    tutorial_notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=True)
    exercise_notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=True)

    course = relationship("Course", back_populates="lessons")


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), primary_key=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="progress")
