from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_teams():
    return {"message": "Team formation endpoint - to be implemented"}
