from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from src.schemas.user import UserResponse
from src.services.internal_user_service import UserService, get_user_service


router = APIRouter()


@router.post(
    "/info",
    response_model=dict[str, dict[str, Any] | list[UserResponse]],
    summary="Внутренняя API: получение списка пользователей",
)
async def get_users_info(
    user_filters: dict[str, Any | list[str]] = None,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    page_size: Annotated[int, Query(le=10_000, description="Записей на странице")] = 100,
    only_user: Annotated[bool, Query(description="Флаг - только с ролью 'пользователь'")] = True,
    user_service: UserService = Depends(get_user_service),
) -> dict[str, dict[str, Any] | list[UserResponse]]:
    """
    Внутренняя API: получение списка пользователей
    """
    return await user_service.get_users_info(
        page_number=page_number,
        page_size=page_size,
        only_user=only_user,
        user_ids=user_filters.get("user_ids"),
    )
