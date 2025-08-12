"""
Course enrollment API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_enrollments():
    """List enrollments - to be implemented."""
    return {"message": "Enrollment management endpoints - implementation in progress"}

@router.post("/")
async def create_enrollment():
    """Create enrollment - to be implemented."""
    return {"message": "Student enrollment endpoint - implementation in progress"}

@router.get("/{enrollment_id}")
async def get_enrollment(enrollment_id: str):
    """Get enrollment details - to be implemented."""
    return {"message": f"Get enrollment {enrollment_id} - implementation in progress"}

@router.put("/{enrollment_id}")
async def update_enrollment(enrollment_id: str):
    """Update enrollment - to be implemented."""
    return {"message": f"Update enrollment {enrollment_id} - implementation in progress"}

@router.delete("/{enrollment_id}")
async def delete_enrollment(enrollment_id: str):
    """Delete enrollment - to be implemented."""
    return {"message": f"Delete enrollment {enrollment_id} - implementation in progress"}
