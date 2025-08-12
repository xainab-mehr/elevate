"""
Users domain entities.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.shared.domain.base import TenantAwareEntity


class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    INSTRUCTOR = "instructor" 
    STUDENT = "student"


class User(TenantAwareEntity):
    """User entity."""
    
    __tablename__ = "users"
    
    # Basic information
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Role and permissions
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    
    # Profile information
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Academic information
    student_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    major: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year_of_study: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Course relationships
    instructor_courses: Mapped[List["CourseInstructor"]] = relationship(
        "CourseInstructor",
        back_populates="instructor",
        cascade="all, delete-orphan"
    )
    student_enrollments: Mapped[List["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def active_instructor_courses(self) -> List["CourseInstructor"]:
        """Get active course instructor assignments."""
        return [ci for ci in self.instructor_courses if ci.is_active]
    
    @property
    def active_student_enrollments(self) -> List["CourseEnrollment"]:
        """Get active student enrollments."""
        from app.courses.domain.entities import EnrollmentStatus
        return [ce for ce in self.student_enrollments if ce.status == EnrollmentStatus.ACTIVE]
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
