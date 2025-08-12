"""
Courses infrastructure repositories.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.shared.domain.base import Repository
from app.courses.domain.entities import (
    Course, CourseInstructor, Project, CourseEnrollment,
    EnrollmentStatus, EnrollmentMethod, InstructorRole
)
from app.courses.domain.repositories import (
    CourseRepositoryInterface,
    CourseInstructorRepositoryInterface,
    ProjectRepositoryInterface,
    CourseEnrollmentRepositoryInterface
)


class CourseRepository(Repository, CourseRepositoryInterface):
    """SQLAlchemy implementation of course repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID."""
        result = await self.session.execute(
            select(Course)
            .options(
                selectinload(Course.instructors),
                selectinload(Course.enrollments),
                selectinload(Course.projects)
            )
            .where(Course.id == course_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_and_tenant(self, course_id: str, tenant_id: str) -> Optional[Course]:
        """Get course by ID and tenant."""
        result = await self.session.execute(
            select(Course)
            .options(
                selectinload(Course.instructors),
                selectinload(Course.enrollments),
                selectinload(Course.projects)
            )
            .where(and_(Course.id == course_id, Course.tenant_id == tenant_id))
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str, tenant_id: str) -> Optional[Course]:
        """Get course by code within tenant."""
        result = await self.session.execute(
            select(Course).where(
                and_(Course.code == code, Course.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, course: Course) -> Course:
        """Create a new course."""
        self.session.add(course)
        await self.session.commit()
        await self.session.refresh(course)
        return course
    
    async def update(self, course: Course) -> Course:
        """Update an existing course."""
        await self.session.commit()
        await self.session.refresh(course)
        return course
    
    async def delete(self, course_id: str) -> bool:
        """Delete a course."""
        course = await self.get_by_id(course_id)
        if course:
            await self.session.delete(course)
            await self.session.commit()
            return True
        return False
    
    async def list_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """List courses within a tenant."""
        result = await self.session.execute(
            select(Course)
            .where(Course.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .order_by(Course.year.desc(), Course.semester, Course.name)
        )
        return list(result.scalars().all())
    
    async def list_by_instructor(self, instructor_id: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """List courses taught by an instructor."""
        result = await self.session.execute(
            select(Course)
            .join(CourseInstructor)
            .where(and_(
                CourseInstructor.instructor_id == instructor_id,
                CourseInstructor.is_active == True,
                Course.tenant_id == tenant_id
            ))
            .offset(skip)
            .limit(limit)
            .order_by(Course.year.desc(), Course.semester, Course.name)
        )
        return list(result.scalars().all())
    
    async def list_by_student(self, student_id: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """List courses a student is enrolled in."""
        result = await self.session.execute(
            select(Course)
            .join(CourseEnrollment)
            .where(and_(
                CourseEnrollment.student_id == student_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE,
                Course.tenant_id == tenant_id
            ))
            .offset(skip)
            .limit(limit)
            .order_by(Course.year.desc(), Course.semester, Course.name)
        )
        return list(result.scalars().all())
    
    async def list_by_department(self, department: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """List courses by department."""
        result = await self.session.execute(
            select(Course)
            .where(and_(
                Course.department == department,
                Course.tenant_id == tenant_id
            ))
            .offset(skip)
            .limit(limit)
            .order_by(Course.year.desc(), Course.semester, Course.name)
        )
        return list(result.scalars().all())
    
    async def search_courses(self, query: str, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """Search courses by name, code, or description."""
        search_term = f"%{query}%"
        result = await self.session.execute(
            select(Course)
            .where(and_(
                Course.tenant_id == tenant_id,
                or_(
                    Course.name.ilike(search_term),
                    Course.code.ilike(search_term),
                    Course.description.ilike(search_term),
                    Course.department.ilike(search_term)
                )
            ))
            .offset(skip)
            .limit(limit)
            .order_by(Course.year.desc(), Course.semester, Course.name)
        )
        return list(result.scalars().all())


class CourseInstructorRepository(Repository, CourseInstructorRepositoryInterface):
    """SQLAlchemy implementation of course instructor repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_id(self, instructor_assignment_id: str) -> Optional[CourseInstructor]:
        """Get course instructor assignment by ID."""
        result = await self.session.execute(
            select(CourseInstructor)
            .options(selectinload(CourseInstructor.course), selectinload(CourseInstructor.instructor))
            .where(CourseInstructor.id == instructor_assignment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_course_and_instructor(self, course_id: str, instructor_id: str) -> List[CourseInstructor]:
        """Get all assignments for a course-instructor pair."""
        result = await self.session.execute(
            select(CourseInstructor)
            .where(and_(
                CourseInstructor.course_id == course_id,
                CourseInstructor.instructor_id == instructor_id
            ))
        )
        return list(result.scalars().all())
    
    async def create(self, course_instructor: CourseInstructor) -> CourseInstructor:
        """Create a new course instructor assignment."""
        self.session.add(course_instructor)
        await self.session.commit()
        await self.session.refresh(course_instructor)
        return course_instructor
    
    async def update(self, course_instructor: CourseInstructor) -> CourseInstructor:
        """Update a course instructor assignment."""
        await self.session.commit()
        await self.session.refresh(course_instructor)
        return course_instructor
    
    async def delete(self, instructor_assignment_id: str) -> bool:
        """Delete a course instructor assignment."""
        assignment = await self.get_by_id(instructor_assignment_id)
        if assignment:
            await self.session.delete(assignment)
            await self.session.commit()
            return True
        return False
    
    async def list_by_course(self, course_id: str) -> List[CourseInstructor]:
        """List all instructors for a course."""
        result = await self.session.execute(
            select(CourseInstructor)
            .options(selectinload(CourseInstructor.instructor))
            .where(and_(
                CourseInstructor.course_id == course_id,
                CourseInstructor.is_active == True
            ))
            .order_by(CourseInstructor.role, CourseInstructor.assigned_at)
        )
        return list(result.scalars().all())
    
    async def list_by_instructor(self, instructor_id: str, tenant_id: str) -> List[CourseInstructor]:
        """List all course assignments for an instructor."""
        result = await self.session.execute(
            select(CourseInstructor)
            .options(selectinload(CourseInstructor.course))
            .where(and_(
                CourseInstructor.instructor_id == instructor_id,
                CourseInstructor.is_active == True,
                CourseInstructor.tenant_id == tenant_id
            ))
            .order_by(CourseInstructor.assigned_at.desc())
        )
        return list(result.scalars().all())
    
    async def check_instructor_permission(self, course_id: str, instructor_id: str) -> bool:
        """Check if instructor has permission to manage a course (ALL ROLES HAVE EQUAL PERMISSIONS)."""
        result = await self.session.execute(
            select(CourseInstructor)
            .where(and_(
                CourseInstructor.course_id == course_id,
                CourseInstructor.instructor_id == instructor_id,
                CourseInstructor.is_active == True
            ))
        )
        return result.scalar_one_or_none() is not None


class ProjectRepository(Repository, ProjectRepositoryInterface):
    """SQLAlchemy implementation of project repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.course))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_and_tenant(self, project_id: str, tenant_id: str) -> Optional[Project]:
        """Get project by ID and tenant."""
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.course))
            .where(and_(Project.id == project_id, Project.tenant_id == tenant_id))
        )
        return result.scalar_one_or_none()
    
    async def create(self, project: Project) -> Project:
        """Create a new project."""
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project
    
    async def update(self, project: Project) -> Project:
        """Update an existing project."""
        await self.session.commit()
        await self.session.refresh(project)
        return project
    
    async def delete(self, project_id: str) -> bool:
        """Delete a project."""
        project = await self.get_by_id(project_id)
        if project:
            await self.session.delete(project)
            await self.session.commit()
            return True
        return False
    
    async def list_by_course(self, course_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """List projects for a course."""
        result = await self.session.execute(
            select(Project)
            .where(Project.course_id == course_id)
            .offset(skip)
            .limit(limit)
            .order_by(Project.due_date.desc())
        )
        return list(result.scalars().all())
    
    async def list_active_projects(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """List active projects across all courses in a tenant."""
        result = await self.session.execute(
            select(Project)
            .where(and_(
                Project.tenant_id == tenant_id,
                Project.is_active == True
            ))
            .offset(skip)
            .limit(limit)
            .order_by(Project.due_date)
        )
        return list(result.scalars().all())
    
    async def list_published_projects(self, course_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """List published projects for a course (visible to students)."""
        result = await self.session.execute(
            select(Project)
            .where(and_(
                Project.course_id == course_id,
                Project.is_published == True,
                Project.is_active == True
            ))
            .offset(skip)
            .limit(limit)
            .order_by(Project.due_date)
        )
        return list(result.scalars().all())
    
    async def list_team_formation_open(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """List projects where team formation is still open."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Project)
            .where(and_(
                Project.tenant_id == tenant_id,
                Project.is_active == True,
                Project.is_published == True,
                Project.team_formation_deadline >= now
            ))
            .offset(skip)
            .limit(limit)
            .order_by(Project.team_formation_deadline)
        )
        return list(result.scalars().all())


class CourseEnrollmentRepository(Repository, CourseEnrollmentRepositoryInterface):
    """SQLAlchemy implementation of course enrollment repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_id(self, enrollment_id: str) -> Optional[CourseEnrollment]:
        """Get enrollment by ID."""
        result = await self.session.execute(
            select(CourseEnrollment)
            .options(selectinload(CourseEnrollment.course), selectinload(CourseEnrollment.student))
            .where(CourseEnrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_course_and_student(self, course_id: str, student_id: str) -> Optional[CourseEnrollment]:
        """Get enrollment for a specific course and student."""
        result = await self.session.execute(
            select(CourseEnrollment)
            .where(and_(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.student_id == student_id
            ))
        )
        return result.scalar_one_or_none()
    
    async def create(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        """Create a new enrollment."""
        self.session.add(enrollment)
        await self.session.commit()
        await self.session.refresh(enrollment)
        return enrollment
    
    async def update(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        """Update an existing enrollment."""
        await self.session.commit()
        await self.session.refresh(enrollment)
        return enrollment
    
    async def delete(self, enrollment_id: str) -> bool:
        """Delete an enrollment."""
        enrollment = await self.get_by_id(enrollment_id)
        if enrollment:
            await self.session.delete(enrollment)
            await self.session.commit()
            return True
        return False
    
    async def list_by_course(self, course_id: str, status: Optional[EnrollmentStatus] = None, skip: int = 0, limit: int = 100) -> List[CourseEnrollment]:
        """List enrollments for a course, optionally filtered by status."""
        query = select(CourseEnrollment).options(selectinload(CourseEnrollment.student))
        
        if status:
            query = query.where(and_(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.status == status
            ))
        else:
            query = query.where(CourseEnrollment.course_id == course_id)
        
        query = query.offset(skip).limit(limit).order_by(CourseEnrollment.enrolled_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def list_by_student(self, student_id: str, tenant_id: str, status: Optional[EnrollmentStatus] = None, skip: int = 0, limit: int = 100) -> List[CourseEnrollment]:
        """List enrollments for a student, optionally filtered by status."""
        query = select(CourseEnrollment).options(selectinload(CourseEnrollment.course))
        
        if status:
            query = query.where(and_(
                CourseEnrollment.student_id == student_id,
                CourseEnrollment.status == status,
                CourseEnrollment.tenant_id == tenant_id
            ))
        else:
            query = query.where(and_(
                CourseEnrollment.student_id == student_id,
                CourseEnrollment.tenant_id == tenant_id
            ))
        
        query = query.offset(skip).limit(limit).order_by(CourseEnrollment.enrolled_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_active_enrollments(self, course_id: str) -> int:
        """Count active enrollments for a course."""
        result = await self.session.execute(
            select(func.count(CourseEnrollment.id))
            .where(and_(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            ))
        )
        return result.scalar_one()
    
    async def list_pending_enrollments(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[CourseEnrollment]:
        """List pending enrollments across all courses in a tenant."""
        result = await self.session.execute(
            select(CourseEnrollment)
            .options(selectinload(CourseEnrollment.course), selectinload(CourseEnrollment.student))
            .where(and_(
                CourseEnrollment.tenant_id == tenant_id,
                CourseEnrollment.status == EnrollmentStatus.PENDING
            ))
            .offset(skip)
            .limit(limit)
            .order_by(CourseEnrollment.enrolled_at)
        )
        return list(result.scalars().all())
    
    async def bulk_enroll_students(self, course_id: str, student_ids: List[str], enrollment_method: str) -> List[CourseEnrollment]:
        """Bulk enroll multiple students."""
        enrollments = []
        for student_id in student_ids:
            enrollment = CourseEnrollment(
                course_id=course_id,
                student_id=student_id,
                status=EnrollmentStatus.ACTIVE,
                enrollment_method=EnrollmentMethod(enrollment_method),
                tenant_id=await self._get_course_tenant_id(course_id),
            )
            self.session.add(enrollment)
            enrollments.append(enrollment)
        
        await self.session.commit()
        
        for enrollment in enrollments:
            await self.session.refresh(enrollment)
        
        return enrollments
    
    async def _get_course_tenant_id(self, course_id: str) -> str:
        """Helper to get tenant_id for a course."""
        result = await self.session.execute(
            select(Course.tenant_id).where(Course.id == course_id)
        )
        return result.scalar_one()
