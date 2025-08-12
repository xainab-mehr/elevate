"""
Tenancy domain services.
"""

from typing import Optional

from app.tenancy.domain.entities import Organization, OrganizationSettings
from app.tenancy.domain.repositories import OrganizationRepositoryInterface


class OrganizationService:
    """Service for organization-related business logic."""
    
    def __init__(self, organization_repo: OrganizationRepositoryInterface):
        self.organization_repo = organization_repo
    
    async def create_organization(
        self,
        name: str,
        slug: str,
        email: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Organization:
        """Create a new organization with validation."""
        
        # Check if slug already exists
        existing_org = await self.organization_repo.get_by_slug(slug)
        if existing_org:
            raise ValueError(f"Organization with slug '{slug}' already exists")
        
        # Check if domain already exists (if provided)
        if domain:
            existing_domain = await self.organization_repo.get_by_domain(domain)
            if existing_domain:
                raise ValueError(f"Organization with domain '{domain}' already exists")
        
        # Create organization
        organization = Organization(
            name=name,
            slug=slug,
            email=email,
            domain=domain,
        )
        
        return await self.organization_repo.create(organization)
    
    async def validate_slug(self, slug: str, exclude_id: Optional[str] = None) -> bool:
        """Validate if slug is available."""
        existing_org = await self.organization_repo.get_by_slug(slug)
        if not existing_org:
            return True
        
        if exclude_id and existing_org.id == exclude_id:
            return True
        
        return False
    
    async def validate_domain(self, domain: str, exclude_id: Optional[str] = None) -> bool:
        """Validate if domain is available."""
        existing_org = await self.organization_repo.get_by_domain(domain)
        if not existing_org:
            return True
        
        if exclude_id and existing_org.id == exclude_id:
            return True
        
        return False
