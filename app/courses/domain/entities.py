"""
Courses domain entities.
"""

import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean, DateTime, String, Text, Integer, ForeignKey, Enum,
    UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.domain.base import TenantAwareEntity


class EnrollmentStatus(enum.Enum):
    """Enrollment status enumeration."""
    PENDING = "pending"           # Awaiting approval
    ACTIVE = "active"             # Currently enrolled
    DROPPED = "dropped"           # Student dropped
    COMPLETED = "completed"       # Course finished


class EnrollmentMethod(enum.Enum):
    """Enrollment method enumeration."""
    SELF_ENROLLED = "self_enrolled"
    INSTRUCTOR_ADDED = "instructor_added"
    CSV_IMPORT = "csv_import"
    ADMIN_ADDED = "admin_added"


class InstructorRole(enum.Enum):
    """Instructor role enumeration - ALL ROLES HAVE EQUAL PERMISSIONS."""
    PRIMARY_INSTRUCTOR = "primary_instructor"
    CO_INSTRUCTOR = "co_instructor"
    TEACHING_ASSISTANT = "teaching_assistant"


class Course(TenantAwareEntity):
    """Course entity representing an academic course."""
    
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_course_code_per_tenant'),
        Index('idx_course_tenant_instructor', 'tenant_id'),
        Index('idx_course_semester_year', 'semester', 'year'),
        Index('idx_course_department', 'department'),
    )
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    semester: Mapped[str] = mapped_column(String(20), nullable=False)  # Fall, Spring, Summer
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Settings & Configuration
    max_students: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enrollment_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    drop_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    instructors: Mapped[List["CourseInstructor"]] = relationship(
        "CourseInstructor",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    enrollments: Mapped[List["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    
    @property
    def current_enrollment_count(self) -> int:
        """Get current number of enrolled students."""
        return len([e for e in self.enrollments if e.status == EnrollmentStatus.ACTIVE])
    
    @property
    def is_full(self) -> bool:
        """Check if course is at capacity."""
        if self.max_students is None:
            return False
        return self.current_enrollment_count >= self.max_students
    
    @property
    def enrollment_open(self) -> bool:
        """Check if enrollment is still open."""
        if not self.is_active:
            return False
        if self.enrollment_deadline and datetime.utcnow() > self.enrollment_deadline:
            return False
        return not self.is_full
    
    def __repr__(self) -> str:
        return f"<Course(id={self.id}, code={self.code}, name={self.name})>"


class CourseInstructor(TenantAwareEntity):
    """Association entity for course-instructor relationships with equal permissions."""
    
    __tablename__ = "course_instructors"
    __table_args__ = (
        UniqueConstraint('course_id', 'instructor_id', 'role', name='uq_course_instructor_role'),
        Index('idx_course_instructor_course', 'course_id'),
        Index('idx_course_instructor_user', 'instructor_id'),
    )
    
    # Relationships
    course_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )
    instructor_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Role and status
    role: Mapped[InstructorRole] = mapped_column(Enum(InstructorRole), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="instructors")
    instructor: Mapped["User"] = relationship("User", back_populates="instructor_courses")
    
    def __repr__(self) -> str:
        return f"<CourseInstructor(course_id={self.course_id}, instructor_id={self.instructor_id}, role={self.role})>"


class Project(TenantAwareEntity):
    """Project entity for team formation activities within courses."""
    
    __tablename__ = "projects"
    __table_args__ = (
        Index('idx_project_course', 'course_id'),
        Index('idx_project_dates', 'start_date', 'due_date'),
        Index('idx_project_status', 'is_active', 'is_published'),
    )
    
    # Basic information
    course_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timeline
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    team_formation_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Team formation settings
    min_team_size: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    max_team_size: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    allow_individual_work: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_team_formation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    manual_team_creation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Status & visibility
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="projects")
    
    @property
    def is_team_formation_open(self) -> bool:
        """Check if team formation is still open."""
        if not self.is_active or not self.is_published:
            return False
        return datetime.utcnow() <= self.team_formation_deadline
    
    @property
    def days_until_due(self) -> int:
        """Calculate days until project due date."""
        delta = self.due_date - datetime.utcnow()
        return max(0, delta.days)
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, course_id={self.course_id})>"


class CourseEnrollment(TenantAwareEntity):
    """Student enrollment in courses."""
    
    __tablename__ = "course_enrollments"
    __table_args__ = (
        UniqueConstraint('course_id', 'student_id', name='uq_course_student_enrollment'),
        Index('idx_enrollment_course', 'course_id'),
        Index('idx_enrollment_student', 'student_id'),
        Index('idx_enrollment_status', 'status'),
        Index('idx_enrollment_method', 'enrollment_method'),
    )
    
    # Core relationship
    course_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )
    student_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Enrollment status and tracking
    status: Mapped[EnrollmentStatus] = mapped_column(Enum(EnrollmentStatus), nullable=False)
    enrollment_method: Mapped[EnrollmentMethod] = mapped_column(Enum(EnrollmentMethod), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    dropped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Additional tracking
    grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # A, B, C, etc.
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    student: Mapped["User"] = relationship("User", back_populates="student_enrollments")
    
    @property
    def is_active(self) -> bool:
        """Check if enrollment is currently active."""
        return self.status == EnrollmentStatus.ACTIVE
    
    @property
    def enrollment_duration_days(self) -> Optional[int]:
        """Calculate how long student has been enrolled."""
        if self.status == EnrollmentStatus.DROPPED and self.dropped_at:
            end_date = self.dropped_at
        elif self.status == EnrollmentStatus.COMPLETED and self.completion_date:
            end_date = self.completion_date
        else:
            end_date = datetime.utcnow()
        
        delta = end_date - self.enrolled_at
        return delta.days
    
    def __repr__(self) -> str:
        return f"<CourseEnrollment(course_id={self.course_id}, student_id={self.student_id}, status={self.status})>"
