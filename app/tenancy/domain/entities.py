"""
Tenancy domain entities for multi-tenant architecture.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.domain.base import BaseEntity


class Organization(BaseEntity):
    """Organization entity representing a tenant (school/institution)."""
    
    __tablename__ = "organizations"
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    # Contact information
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Settings
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Subscription information
    subscription_plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Limits
    max_users: Mapped[Optional[int]] = mapped_column(nullable=True)
    max_courses: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"


class OrganizationSettings(BaseEntity):
    """Organization-specific settings and configurations."""
    
    __tablename__ = "organization_settings"
    
    organization_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Feature flags
    enable_team_formation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_analytics: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_integrations: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Team formation settings
    default_team_size_min: Mapped[int] = mapped_column(default=3, nullable=False)
    default_team_size_max: Mapped[int] = mapped_column(default=6, nullable=False)
    algorithm_timeout_seconds: Mapped[int] = mapped_column(default=30, nullable=False)
    
    # Questionnaire settings
    require_belbin_assessment: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    require_skill_assessment: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    require_schedule_availability: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Integration settings
    canvas_api_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    canvas_api_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    moodle_api_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    moodle_api_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    def __repr__(self) -> str:
        return f"<OrganizationSettings(id={self.id}, org_id={self.organization_id})>"
