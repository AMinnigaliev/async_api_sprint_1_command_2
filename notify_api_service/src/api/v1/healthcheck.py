from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def root():
    return {"message": "User activity API is running"}
