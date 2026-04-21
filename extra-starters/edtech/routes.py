from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    title: str
    description: str
    category: str
    difficulty: Optional[str] = "beginner"
    thumbnail: Optional[str] = None

class LessonCreate(BaseModel):
    course_id: int
    title: str
    content: str
    video_url: Optional[str] = None
    order: Optional[int] = 0
    duration_min: Optional[int] = None

class QuizCreate(BaseModel):
    lesson_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    answer: str           # "a", "b", "c", or "d"
    explanation: Optional[str] = None

class QuizAnswer(BaseModel):
    selected: str         # "a", "b", "c", or "d"

# ── Routes ────────────────────────────────────────────────────────

@router.post("/courses")
def create_course(data: CourseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Course
    course = Course(**data.model_dump(), created_by=user.id)
    db.add(course); db.commit(); db.refresh(course)
    return course

@router.get("/courses")
def list_courses(category: Optional[str] = None, difficulty: Optional[str] = None, db: Session = Depends(get_db)):
    from extra_starters.edtech.models import Course
    q = db.query(Course).filter(Course.is_published == True)
    if category:   q = q.filter(Course.category == category)
    if difficulty: q = q.filter(Course.difficulty == difficulty)
    return q.all()

@router.get("/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    from extra_starters.edtech.models import Course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404, "Course not found")
    return course

@router.post("/courses/{course_id}/enroll")
def enroll(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Enrollment
    existing = db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.course_id == course_id).first()
    if existing:
        return existing
    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.add(enrollment); db.commit(); db.refresh(enrollment)
    return enrollment

@router.get("/my-courses")
def my_courses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Enrollment
    return db.query(Enrollment).filter(Enrollment.user_id == user.id).all()

@router.put("/enrollments/{course_id}/progress")
def update_progress(course_id: int, progress: float, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Enrollment
    enrollment = db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.course_id == course_id).first()
    if not enrollment:
        raise HTTPException(404, "Not enrolled")
    enrollment.progress_pct = min(progress, 100.0)
    enrollment.completed = progress >= 100.0
    db.commit(); db.refresh(enrollment)
    return enrollment

@router.post("/lessons")
def add_lesson(data: LessonCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Lesson
    lesson = Lesson(**data.model_dump())
    db.add(lesson); db.commit(); db.refresh(lesson)
    return lesson

@router.get("/lessons/{course_id}")
def get_lessons(course_id: int, db: Session = Depends(get_db)):
    from extra_starters.edtech.models import Lesson
    return db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()

@router.post("/quizzes")
def create_quiz(data: QuizCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Quiz
    quiz = Quiz(**data.model_dump())
    db.add(quiz); db.commit(); db.refresh(quiz)
    return quiz

@router.post("/quizzes/{quiz_id}/attempt")
def attempt_quiz(quiz_id: int, data: QuizAnswer, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Quiz, QuizAttempt
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    is_correct = data.selected.lower() == quiz.answer.lower()
    attempt = QuizAttempt(user_id=user.id, quiz_id=quiz_id, selected=data.selected, is_correct=is_correct)
    db.add(attempt); db.commit()
    return {"correct": is_correct, "explanation": quiz.explanation, "correct_answer": quiz.answer}

@router.get("/progress/summary")
def progress_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.edtech.models import Enrollment, QuizAttempt
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == user.id).all()
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).all()
    correct = sum(1 for a in attempts if a.is_correct)
    return {
        "courses_enrolled": len(enrollments),
        "courses_completed": sum(1 for e in enrollments if e.completed),
        "quizzes_attempted": len(attempts),
        "quizzes_correct": correct,
        "accuracy_pct": round(correct / len(attempts) * 100, 1) if attempts else 0
    }
