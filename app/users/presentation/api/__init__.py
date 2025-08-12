"""
Users API endpoints.
"""

from fastapi import APIRouter

# Placeholder router for users
router = APIRouter()

@router.get("/")
async def list_users():
    """List users - placeholder."""
    return {"message": "Users endpoint - to be implemented"}
