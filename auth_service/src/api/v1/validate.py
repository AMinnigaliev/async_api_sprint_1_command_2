from fastapi import APIRouter, Body, Depends

from src.schemas.payload import PayloadResponse
from src.services.validate_service import ValidateService, get_validate_service

router = APIRouter()


@router.post(
    "/validate",
    response_model=PayloadResponse,
    summary="Валидация токена пользователя",
    description="Валидация предоставленного токена пользователя. "
                "Возвращает payload токена."
)
async def validate_token(
    token: str = Body(..., embed=True),
    validate_service: ValidateService = Depends(get_validate_service),
) -> PayloadResponse:
    """Валидация токена пользователя"""
    return await validate_service.validate_token(token)
