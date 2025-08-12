"""
Courses API endpoints.
"""

from fastapi import APIRouter

from app.courses.presentation.api.courses import router as courses_router
from app.courses.presentation.api.projects import router as projects_router
from app.courses.presentation.api.enrollments import router as enrollments_router

router = APIRouter()

router.include_router(courses_router, prefix="/courses", tags=["courses"])
router.include_router(projects_router, prefix="/projects", tags=["projects"])
router.include_router(enrollments_router, prefix="/enrollments", tags=["enrollments"])
