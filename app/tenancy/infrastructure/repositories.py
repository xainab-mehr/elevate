"""
Tenancy infrastructure repositories.
"""

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.base import Repository
from app.tenancy.domain.entities import Organization, OrganizationSettings
from app.tenancy.domain.repositories import OrganizationRepositoryInterface


class OrganizationRepository(Repository, OrganizationRepositoryInterface):
    """SQLAlchemy implementation of organization repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_id(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        result = await self.session.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        result = await self.session.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_by_domain(self, domain: str) -> Optional[Organization]:
        """Get organization by domain."""
        result = await self.session.execute(
            select(Organization).where(Organization.domain == domain)
        )
        return result.scalar_one_or_none()
    
    async def create(self, organization: Organization) -> Organization:
        """Create a new organization."""
        self.session.add(organization)
        await self.session.commit()
        await self.session.refresh(organization)
        return organization
    
    async def update(self, organization: Organization) -> Organization:
        """Update an existing organization."""
        await self.session.commit()
        await self.session.refresh(organization)
        return organization
    
    async def delete(self, organization_id: str) -> bool:
        """Delete an organization."""
        organization = await self.get_by_id(organization_id)
        if organization:
            await self.session.delete(organization)
            await self.session.commit()
            return True
        return False
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """List all organizations with pagination."""
        result = await self.session.execute(
            select(Organization)
            .offset(skip)
            .limit(limit)
            .order_by(Organization.created_at.desc())
        )
        return result.scalars().all()
