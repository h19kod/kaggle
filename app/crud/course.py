from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.course import Course, Lesson, UserCourseProgress
from app.schemas.course import CourseCreate, CourseUpdate, LessonCreate, LessonUpdate, UserCourseProgressCreate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_difficulty(self, db: Session, *, difficulty: str, skip: int = 0, limit: int = 100) -> List[Course]:
        return (
            db.query(Course)
            .filter(Course.difficulty == difficulty)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDLesson(CRUDBase[Lesson, LessonCreate, LessonUpdate]):
    def get_by_course(self, db: Session, *, course_id: int) -> List[Lesson]:
        return (
            db.query(Lesson)
            .filter(Lesson.course_id == course_id)
            .order_by(Lesson.order_index.asc())
            .all()
        )


class CRUDUserCourseProgress(CRUDBase[UserCourseProgress, UserCourseProgressCreate, UserCourseProgressCreate]):
    def get_by_user(self, db: Session, *, user_id: int) -> List[UserCourseProgress]:
        return db.query(UserCourseProgress).filter(UserCourseProgress.user_id == user_id).all()

    def get_by_user_and_lesson(self, db: Session, *, user_id: int, lesson_id: int) -> Optional[UserCourseProgress]:
        return (
            db.query(UserCourseProgress)
            .filter(UserCourseProgress.user_id == user_id, UserCourseProgress.lesson_id == lesson_id)
            .first()
        )


course_crud = CRUDCourse(Course)
lesson_crud = CRUDLesson(Lesson)
user_course_progress_crud = CRUDUserCourseProgress(UserCourseProgress)
