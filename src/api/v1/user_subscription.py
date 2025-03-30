from uuid import UUID

from fastapi import APIRouter, Depends

from src.dependencies.auth import role_dependency
from src.models.subscription import Subscription
from src.models.user import User, UserRoleEnum
from src.schemas.subscription import SubscriptionResponse
from src.schemas.user import UserResponse
from src.services.user_subscription_service import (
    UserSubscriptionService, get_user_subscription_service)

router = APIRouter(
    dependencies=[Depends(role_dependency(
        (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN,)
    ))]
)


@router.post(
    "/{user_id}/subscribe/{subscription_id}",
    response_model=UserResponse,
    summary="Подписка пользователя",
    description="Добавляет подписку пользователю, если её ещё нет.",
)
async def assign_subscription(
    user_id: UUID,
    subscription_id: UUID,
    user_subscription_service: UserSubscriptionService = Depends(
        get_user_subscription_service
    ),
) -> User:
    """Эндпоинт для назначения подписки пользователю."""
    return await user_subscription_service.assign_subscription(
        user_id, subscription_id
    )


@router.delete(
    "/{user_id}/unsubscribe/{subscription_id}",
    response_model=UserResponse,
    summary="Отмена подписки",
    description="Удаляет подписку у пользователя, если она была.",
)
async def remove_subscription(
    user_id: UUID,
    subscription_id: UUID,
    user_subscription_service: UserSubscriptionService = Depends(
        get_user_subscription_service
    ),
) -> User:
    """Эндпоинт для отмены подписки у пользователя."""
    return await user_subscription_service.remove_subscription(
        user_id, subscription_id
    )


@router.get(
    "/{user_id}/subscriptions",
    response_model=list[SubscriptionResponse],
    summary="Список подписок пользователя",
    description="Возвращает список всех подписок пользователя.",
)
async def get_user_subscriptions(
    user_id: UUID,
    user_subscription_service: UserSubscriptionService = Depends(
        get_user_subscription_service
    ),
) -> list[Subscription]:
    """Эндпоинт для получения списка подписок пользователя."""
    return await user_subscription_service.get_user_subscriptions(user_id)
