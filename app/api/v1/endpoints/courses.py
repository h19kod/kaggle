from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.crud.course import course_crud, lesson_crud, user_course_progress_crud
from app.models.user import User
from app.schemas.course import Course, CourseCreate, CourseUpdate, Lesson, LessonCreate, LessonUpdate, UserCourseProgress, UserCourseProgressCreate

router = APIRouter()
lessons_router = APIRouter()


@router.get("/", response_model=List[Course])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return course_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=Course)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return course_crud.create(db, obj_in=course_in)


@router.get("/{course_id}", response_model=Course)
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = course_crud.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=Course)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = course_crud.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course_crud.update(db, db_obj=course, obj_in=course_in)


@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    course = course_crud.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course_crud.remove(db, id=course_id)
    return {"message": "Course deleted"}


@router.get("/{course_id}/lessons", response_model=List[Lesson])
def list_lessons(course_id: int, db: Session = Depends(get_db)):
    return lesson_crud.get_by_course(db, course_id=course_id)


@router.post("/{course_id}/lessons", response_model=Lesson)
def create_lesson(
    course_id: int,
    lesson_in: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    course = course_crud.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson_in.course_id = course_id
    return lesson_crud.create(db, obj_in=lesson_in)


@router.get("/lessons/{lesson_id}", response_model=Lesson)
def read_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = lesson_crud.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.put("/lessons/{lesson_id}", response_model=Lesson)
def update_lesson(
    lesson_id: int,
    lesson_in: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lesson = lesson_crud.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson_crud.update(db, db_obj=lesson, obj_in=lesson_in)


@lessons_router.post("/{lesson_id}/complete")
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = user_course_progress_crud.get_by_user_and_lesson(db, user_id=current_user.id, lesson_id=lesson_id)
    if existing:
        raise HTTPException(status_code=400, detail="Lesson already completed")
    progress_in = UserCourseProgressCreate(user_id=current_user.id, lesson_id=lesson_id)
    return user_course_progress_crud.create(db, obj_in=progress_in)
