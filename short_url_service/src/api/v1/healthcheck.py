from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def root():
    return {"message": "Short url API is running"}
