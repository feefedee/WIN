# Theme: EdTech

## Likely problem statements
- Online learning platform
- Adaptive quiz system
- Student progress tracker
- Personalized course recommender
- Smart classroom / attendance system

## Your models (already built)
- Course — title, category, difficulty, published flag
- Lesson — content, video URL, order
- Enrollment — tracks user ↔ course with progress %
- Quiz — MCQ with 4 options, correct answer, explanation
- QuizAttempt — records each answer + correct/wrong

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /edu/courses | Create a course |
| GET  | /edu/courses?category=coding | Browse courses |
| GET  | /edu/courses/{id} | Course detail |
| POST | /edu/courses/{id}/enroll | Enroll in a course |
| GET  | /edu/my-courses | My enrolled courses |
| PUT  | /edu/enrollments/{id}/progress | Update progress % |
| POST | /edu/lessons | Add lesson to course |
| GET  | /edu/lessons/{course_id} | All lessons in order |
| POST | /edu/quizzes | Create MCQ quiz |
| POST | /edu/quizzes/{id}/attempt | Submit answer → get result |
| GET  | /edu/progress/summary | My stats (accuracy, completion) |

## How to plug into main.py
```python
from extra_starters.edtech.routes import router as edu_router
app.include_router(edu_router, prefix="/edu", tags=["EdTech"])
```
