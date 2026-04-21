from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class DifficultyLevel(str, enum.Enum):
    beginner     = "beginner"
    intermediate = "intermediate"
    advanced     = "advanced"


class Course(Base):
    __tablename__ = "courses"

    id          = Column(Integer, primary_key=True, index=True)
    created_by  = Column(Integer, ForeignKey("users.id"))
    title       = Column(String)
    description = Column(Text)
    category    = Column(String)       # math, science, coding, language, etc.
    difficulty  = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)
    thumbnail   = Column(String, nullable=True)
    is_published= Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    lessons     = relationship("Lesson", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"

    id          = Column(Integer, primary_key=True, index=True)
    course_id   = Column(Integer, ForeignKey("courses.id"))
    title       = Column(String)
    content     = Column(Text)
    video_url   = Column(String, nullable=True)
    order       = Column(Integer, default=0)
    duration_min= Column(Integer, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    course      = relationship("Course", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    course_id    = Column(Integer, ForeignKey("courses.id"))
    progress_pct = Column(Float, default=0.0)    # 0-100
    completed    = Column(Boolean, default=False)
    enrolled_at  = Column(DateTime(timezone=True), server_default=func.now())

    course       = relationship("Course", back_populates="enrollments")


class Quiz(Base):
    __tablename__ = "quizzes"

    id          = Column(Integer, primary_key=True, index=True)
    lesson_id   = Column(Integer, ForeignKey("lessons.id"))
    question    = Column(Text)
    option_a    = Column(String)
    option_b    = Column(String)
    option_c    = Column(String)
    option_d    = Column(String)
    answer      = Column(String)      # "a", "b", "c", or "d"
    explanation = Column(Text, nullable=True)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    quiz_id     = Column(Integer, ForeignKey("quizzes.id"))
    selected    = Column(String)      # "a", "b", "c", or "d"
    is_correct  = Column(Boolean)
    attempted_at= Column(DateTime(timezone=True), server_default=func.now())
