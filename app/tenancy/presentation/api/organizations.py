"""
Organization API endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.tenancy.domain.services import OrganizationService
from app.tenancy.infrastructure.repositories import OrganizationRepository
from app.tenancy.presentation.schemas import (
    Organization,
    OrganizationCreate,
    OrganizationList,
    OrganizationUpdate,
)
from app.users.domain.entities import User

router = APIRouter()


def get_organization_service(db: AsyncSession = Depends(get_db)) -> OrganizationService:
    """Get organization service."""
    org_repo = OrganizationRepository(db)
    return OrganizationService(org_repo)


@router.get("/", response_model=OrganizationList)
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    service: OrganizationService = Depends(get_organization_service),
):
    """List all organizations (admin only)."""
    organizations = await service.organization_repo.list_all(skip=skip, limit=limit)
    
    return OrganizationList(
        organizations=organizations,
        total=len(organizations),  # TODO: Add proper count query
        page=skip // limit + 1,
        size=len(organizations),
    )


@router.post("/", response_model=Organization, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization_data: OrganizationCreate,
    current_user: User = Depends(get_current_admin),
    service: OrganizationService = Depends(get_organization_service),
):
    """Create a new organization (admin only)."""
    try:
        organization = await service.create_organization(
            name=organization_data.name,
            slug=organization_data.slug,
            email=organization_data.email,
            domain=organization_data.domain,
        )
        return organization
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{organization_id}", response_model=Organization)
async def get_organization(
    organization_id: str,
    current_user: User = Depends(get_current_admin),
    service: OrganizationService = Depends(get_organization_service),
):
    """Get organization by ID (admin only)."""
    organization = await service.organization_repo.get_by_id(organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization


@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
    organization_id: str,
    organization_data: OrganizationUpdate,
    current_user: User = Depends(get_current_admin),
    service: OrganizationService = Depends(get_organization_service),
):
    """Update organization (admin only)."""
    organization = await service.organization_repo.get_by_id(organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update fields
    update_data = organization_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    updated_organization = await service.organization_repo.update(organization)
    return updated_organization


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: str,
    current_user: User = Depends(get_current_admin),
    service: OrganizationService = Depends(get_organization_service),
):
    """Delete organization (admin only)."""
    success = await service.organization_repo.delete(organization_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
