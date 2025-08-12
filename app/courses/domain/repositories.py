"""
Courses domain repository interfaces.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.courses.domain.entities import (
    Course, CourseInstructor, Project, CourseEnrollment,
    EnrollmentStatus, InstructorRole
)


class CourseRepositoryInterface(ABC):
    """Course repository interface."""
    
    @abstractmethod
    async def get_by_id(self, course_id: str) -> Optional[Course]:
        pass
    
    @abstractmethod
    async def get_by_id_and_tenant(self, course_id: str, tenant_id: str) -> Optional[Course]:
        pass
    
    @abstractmethod
    async def get_by_code(self, code: str, tenant_id: str) -> Optional[Course]:
        pass
    
    @abstractmethod
    async def create(self, course: Course) -> Course:
        pass
    
    @abstractmethod
    async def update(self, course: Course) -> Course:
        pass
    
    @abstractmethod
    async def delete(self, course_id: str) -> bool:
        pass
    
    @abstractmethod
    async def list_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        pass
    
    @abstractmethod
    async def list_by_instructor(self, instructor_id: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        pass
    
    @abstractmethod
    async def list_by_student(self, student_id: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        pass
    
    @abstractmethod
    async def list_by_department(self, department: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        pass
    
    @abstractmethod
    async def search_courses(self, query: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        pass


class CourseInstructorRepositoryInterface(ABC):
    """Course instructor association repository interface."""
    
    @abstractmethod
    async def get_by_id(self, instructor_assignment_id: str) -> Optional[CourseInstructor]:
        pass
    
    @abstractmethod
    async def get_by_course_and_instructor(self, course_id: str, instructor_id: str) -> List[CourseInstructor]:
        pass
    
    @abstractmethod
    async def create(self, course_instructor: CourseInstructor) -> CourseInstructor:
        pass
    
    @abstractmethod
    async def update(self, course_instructor: CourseInstructor) -> CourseInstructor:
        pass
    
    @abstractmethod
    async def delete(self, instructor_assignment_id: str) -> bool:
        pass
    
    @abstractmethod
    async def list_by_course(self, course_id: str) -> List[CourseInstructor]:
        pass
    
    @abstractmethod
    async def list_by_instructor(self, instructor_id: str, tenant_id: str) -> List[CourseInstructor]:
        pass
    
    @abstractmethod
    async def check_instructor_permission(self, course_id: str, instructor_id: str) -> bool:
        pass


class ProjectRepositoryInterface(ABC):
    """Project repository interface."""
    
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        pass
    
    @abstractmethod
    async def get_by_id_and_tenant(self, project_id: str, tenant_id: str) -> Optional[Project]:
        pass
    
    @abstractmethod
    async def create(self, project: Project) -> Project:
        pass
    
    @abstractmethod
    async def update(self, project: Project) -> Project:
        pass
    
    @abstractmethod
    async def delete(self, project_id: str) -> bool:
        pass
    
    @abstractmethod
    async def list_by_course(self, course_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        pass
    
    @abstractmethod
    async def list_active_projects(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        pass
    
    @abstractmethod
    async def list_published_projects(self, course_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        pass
    
    @abstractmethod
    async def list_team_formation_open(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        pass


class CourseEnrollmentRepositoryInterface(ABC):
    """Course enrollment repository interface."""
    
    @abstractmethod
    async def get_by_id(self, enrollment_id: str) -> Optional[CourseEnrollment]:
        pass
    
    @abstractmethod
    async def get_by_course_and_student(self, course_id: str, student_id: str) -> Optional[CourseEnrollment]:
        pass
    
    @abstractmethod
    async def create(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        pass
    
    @abstractmethod
    async def update(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        pass
    
    @abstractmethod
    async def delete(self, enrollment_id: str) -> bool:
        pass
    
    @abstractmethod
    async def list_by_course(self, course_id: str, status: Optional[EnrollmentStatus] = None, skip: int = 0, limit: int = 100) -> List[CourseEnrollment]:
        pass
    
    @abstractmethod
    async def list_by_student(self, student_id: str, tenant_id: str, status: Optional[EnrollmentStatus] = None, skip: int = 0, limit: int = 100) -> List[CourseEnrollment]:
        pass
    
    @abstractmethod
    async def count_active_enrollments(self, course_id: str) -> int:
        pass
    
    @abstractmethod
    async def list_pending_enrollments(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[CourseEnrollment]:
        pass
    
    @abstractmethod
    async def bulk_enroll_students(self, course_id: str, student_ids: List[str], enrollment_method: str) -> List[CourseEnrollment]:
        pass
