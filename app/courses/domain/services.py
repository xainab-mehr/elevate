"""
Courses domain services.
"""

from datetime import datetime
from typing import List, Optional

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


class CourseService:
    """Service for course-related business logic."""
    
    def __init__(
        self,
        course_repo: CourseRepositoryInterface,
        instructor_repo: CourseInstructorRepositoryInterface,
        enrollment_repo: CourseEnrollmentRepositoryInterface,
    ):
        self.course_repo = course_repo
        self.instructor_repo = instructor_repo
        self.enrollment_repo = enrollment_repo
    
    async def create_course(
        self,
        name: str,
        code: str,
        department: str,
        semester: str,
        year: int,
        tenant_id: str,
        primary_instructor_id: str,
        description: Optional[str] = None,
        max_students: Optional[int] = None,
    ) -> Course:
        """Create a new course with a primary instructor."""
        
        # Check if course code already exists in this organization
        existing_course = await self.course_repo.get_by_code(code, tenant_id)
        if existing_course:
            raise ValueError(f"Course with code '{code}' already exists in this organization")
        
        # Create course
        course = Course(
            name=name,
            code=code,
            description=description,
            semester=semester,
            year=year,
            department=department,
            max_students=max_students,
            tenant_id=tenant_id,
        )
        
        created_course = await self.course_repo.create(course)
        
        # Assign primary instructor
        course_instructor = CourseInstructor(
            course_id=created_course.id,
            instructor_id=primary_instructor_id,
            role=InstructorRole.PRIMARY_INSTRUCTOR,
            tenant_id=tenant_id,
        )
        
        await self.instructor_repo.create(course_instructor)
        
        return created_course
    
    async def add_instructor(
        self,
        course_id: str,
        instructor_id: str,
        role: InstructorRole,
        tenant_id: str,
    ) -> CourseInstructor:
        """Add an instructor to a course."""
        
        # Check if instructor is already assigned to this course with this role
        existing_assignments = await self.instructor_repo.get_by_course_and_instructor(
            course_id, instructor_id
        )
        
        for assignment in existing_assignments:
            if assignment.role == role and assignment.is_active:
                raise ValueError(f"Instructor already has role '{role.value}' in this course")
        
        course_instructor = CourseInstructor(
            course_id=course_id,
            instructor_id=instructor_id,
            role=role,
            tenant_id=tenant_id,
        )
        
        return await self.instructor_repo.create(course_instructor)
    
    async def enroll_student(
        self,
        course_id: str,
        student_id: str,
        tenant_id: str,
        enrollment_method: EnrollmentMethod = EnrollmentMethod.SELF_ENROLLED,
        auto_approve: bool = False,
    ) -> CourseEnrollment:
        """Enroll a student in a course."""
        
        # Check if student is already enrolled
        existing_enrollment = await self.enrollment_repo.get_by_course_and_student(
            course_id, student_id
        )
        if existing_enrollment and existing_enrollment.status == EnrollmentStatus.ACTIVE:
            raise ValueError("Student is already enrolled in this course")
        
        # Get course to check capacity and settings
        course = await self.course_repo.get_by_id_and_tenant(course_id, tenant_id)
        if not course:
            raise ValueError("Course not found")
        
        if not course.enrollment_open:
            raise ValueError("Enrollment is closed for this course")
        
        # Determine enrollment status
        if auto_approve or course.auto_approval:
            status = EnrollmentStatus.ACTIVE
        else:
            status = EnrollmentStatus.PENDING
        
        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=student_id,
            status=status,
            enrollment_method=enrollment_method,
            tenant_id=tenant_id,
        )
        
        return await self.enrollment_repo.create(enrollment)
    
    async def approve_enrollment(self, enrollment_id: str) -> CourseEnrollment:
        """Approve a pending enrollment."""
        
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")
        
        if enrollment.status != EnrollmentStatus.PENDING:
            raise ValueError("Only pending enrollments can be approved")
        
        # Check course capacity again
        course = await self.course_repo.get_by_id(enrollment.course_id)
        if course and course.is_full:
            raise ValueError("Course is at capacity")
        
        enrollment.status = EnrollmentStatus.ACTIVE
        return await self.enrollment_repo.update(enrollment)
    
    async def drop_student(self, enrollment_id: str) -> CourseEnrollment:
        """Drop a student from a course."""
        
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")
        
        if enrollment.status not in [EnrollmentStatus.ACTIVE, EnrollmentStatus.PENDING]:
            raise ValueError("Cannot drop student with current enrollment status")
        
        enrollment.status = EnrollmentStatus.DROPPED
        enrollment.dropped_at = datetime.utcnow()
        
        return await self.enrollment_repo.update(enrollment)
    
    async def bulk_enroll_students(
        self,
        course_id: str,
        student_ids: List[str],
        tenant_id: str,
        enrollment_method: EnrollmentMethod = EnrollmentMethod.INSTRUCTOR_ADDED,
    ) -> List[CourseEnrollment]:
        """Bulk enroll multiple students in a course."""
        
        course = await self.course_repo.get_by_id_and_tenant(course_id, tenant_id)
        if not course:
            raise ValueError("Course not found")
        
        # Filter out students who are already enrolled
        enrollments = []
        for student_id in student_ids:
            existing = await self.enrollment_repo.get_by_course_and_student(course_id, student_id)
            if not existing or existing.status != EnrollmentStatus.ACTIVE:
                enrollment = CourseEnrollment(
                    course_id=course_id,
                    student_id=student_id,
                    status=EnrollmentStatus.ACTIVE,  # Auto-approve bulk enrollments
                    enrollment_method=enrollment_method,
                    tenant_id=tenant_id,
                )
                enrollments.append(enrollment)
        
        return await self.enrollment_repo.bulk_enroll_students(
            course_id, [e.student_id for e in enrollments], enrollment_method.value
        )


class ProjectService:
    """Service for project-related business logic."""
    
    def __init__(
        self,
        project_repo: ProjectRepositoryInterface,
        instructor_repo: CourseInstructorRepositoryInterface,
    ):
        self.project_repo = project_repo
        self.instructor_repo = instructor_repo
    
    async def create_project(
        self,
        course_id: str,
        name: str,
        start_date: datetime,
        due_date: datetime,
        team_formation_deadline: datetime,
        tenant_id: str,
        instructor_id: str,
        description: Optional[str] = None,
        min_team_size: int = 3,
        max_team_size: int = 6,
    ) -> Project:
        """Create a new project."""
        
        # Verify instructor has permission to create projects in this course
        has_permission = await self.instructor_repo.check_instructor_permission(
            course_id, instructor_id
        )
        if not has_permission:
            raise ValueError("Instructor does not have permission to create projects in this course")
        
        # Validate dates
        if start_date >= due_date:
            raise ValueError("Start date must be before due date")
        
        if team_formation_deadline > due_date:
            raise ValueError("Team formation deadline must be before or equal to due date")
        
        if min_team_size > max_team_size:
            raise ValueError("Minimum team size cannot be greater than maximum team size")
        
        project = Project(
            course_id=course_id,
            name=name,
            description=description,
            start_date=start_date,
            due_date=due_date,
            team_formation_deadline=team_formation_deadline,
            min_team_size=min_team_size,
            max_team_size=max_team_size,
            tenant_id=tenant_id,
        )
        
        return await self.project_repo.create(project)
    
    async def publish_project(self, project_id: str, instructor_id: str) -> Project:
        """Publish a project to make it visible to students."""
        
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        
        # Verify instructor has permission
        has_permission = await self.instructor_repo.check_instructor_permission(
            project.course_id, instructor_id
        )
        if not has_permission:
            raise ValueError("Instructor does not have permission to publish this project")
        
        project.is_published = True
        return await self.project_repo.update(project)
    
    async def update_team_formation_settings(
        self,
        project_id: str,
        instructor_id: str,
        min_team_size: Optional[int] = None,
        max_team_size: Optional[int] = None,
        team_formation_deadline: Optional[datetime] = None,
        allow_individual_work: Optional[bool] = None,
        auto_team_formation: Optional[bool] = None,
    ) -> Project:
        """Update team formation settings for a project."""
        
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        
        # Verify instructor has permission
        has_permission = await self.instructor_repo.check_instructor_permission(
            project.course_id, instructor_id
        )
        if not has_permission:
            raise ValueError("Instructor does not have permission to modify this project")
        
        # Update settings
        if min_team_size is not None:
            project.min_team_size = min_team_size
        if max_team_size is not None:
            project.max_team_size = max_team_size
        if team_formation_deadline is not None:
            project.team_formation_deadline = team_formation_deadline
        if allow_individual_work is not None:
            project.allow_individual_work = allow_individual_work
        if auto_team_formation is not None:
            project.auto_team_formation = auto_team_formation
        
        # Validate updated settings
        if project.min_team_size > project.max_team_size:
            raise ValueError("Minimum team size cannot be greater than maximum team size")
        
        if project.team_formation_deadline > project.due_date:
            raise ValueError("Team formation deadline must be before or equal to due date")
        
        return await self.project_repo.update(project)
