from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class LessonBase(BaseModel):
    course_id: int
    order_index: int
    title: str
    text_content: Optional[str] = None
    tutorial_notebook_id: Optional[int] = None
    exercise_notebook_id: Optional[int] = None


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    order_index: Optional[int] = None
    title: Optional[str] = None
    text_content: Optional[str] = None
    tutorial_notebook_id: Optional[int] = None
    exercise_notebook_id: Optional[int] = None


class Lesson(LessonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseBase(BaseModel):
    title: str
    summary: Optional[str] = None
    difficulty: Optional[str] = "Beginner"


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    difficulty: Optional[str] = None


class Course(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    lessons: Optional[List[Lesson]] = None


class UserCourseProgressBase(BaseModel):
    user_id: int
    lesson_id: int


class UserCourseProgressCreate(UserCourseProgressBase):
    pass


class UserCourseProgress(UserCourseProgressBase):
    model_config = ConfigDict(from_attributes=True)
    is_completed: bool
    completed_at: Optional[datetime] = None
