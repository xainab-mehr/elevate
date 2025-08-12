from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_courses():
    return {"message": "Courses endpoint - to be implemented"}
