from uuid import UUID

from fastapi import APIRouter, Depends

from src.dependencies.auth import role_dependency
from src.models.subscription import Subscription
from src.models.user import UserRoleEnum
from src.schemas.subscription import SubscriptionCreateUpdate
from src.schemas.user import SubscriptionResponse
from src.services.subscription_service import (SubscriptionService,
                                               get_subscription_service)

router = APIRouter(
    dependencies=[Depends(role_dependency(
        (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN,)
    ))]
)


@router.get(
    "/",
    response_model=list[SubscriptionResponse],
    summary="Список существующих подписок",
    description="Возвращает список всех подписок."
)
async def get_subscriptions(
    subscription_service: SubscriptionService = Depends(
        get_subscription_service
    ),
) -> list[Subscription]:
    """Эндпоинт для получения всех подписок."""
    return await subscription_service.get_subscriptions()


@router.post(
    "/",
    response_model=SubscriptionResponse,
    summary="Создание подписки",
    description="Создает новую подписку на основе переданных данных.",
)
async def create_subscription(
    create_data: SubscriptionCreateUpdate,
    subscription_service: SubscriptionService = Depends(
        get_subscription_service
    ),
) -> Subscription:
    """Эндпоинт для создания новой подписки."""
    return await subscription_service.create_subscription(create_data)


@router.put(
    "/{subscription_id}",
    response_model=SubscriptionResponse,
    summary="Обновление подписки",
    description="Обновляет подписку с заданным идентификатором на основе "
                "переданных данных.",
)
async def subscription_update(
    subscription_id: UUID,
    update_data: SubscriptionCreateUpdate,
    subscription_service: SubscriptionService = Depends(
        get_subscription_service
    ),
) -> Subscription:
    """Эндпоинт для изменения подписки."""
    return await subscription_service.subscription_update(
        subscription_id, update_data
    )


@router.delete(
    "/{subscription_id}",
    summary="Удаление подписки",
    description="Удаляет подписку с заданным идентификатором.",
)
async def delete_subscription(
    subscription_id: UUID,
    subscription_service: SubscriptionService = Depends(
        get_subscription_service
    ),
) -> dict:
    """Эндпоинт для удаления подписки."""
    return await subscription_service.delete_subscription(subscription_id)
