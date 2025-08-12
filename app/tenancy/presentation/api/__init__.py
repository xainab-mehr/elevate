"""
Tenancy API endpoints.
"""

from fastapi import APIRouter

from app.tenancy.presentation.api.organizations import router as organizations_router

router = APIRouter()

router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
