import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.models.subscription import Subscription
from src.models.user import User
from src.repositories.user import get_user_by_id

logger = logging.getLogger(__name__)


class UserSubscriptionService:
    """Сервис для работы с подписками пользователей."""

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def assign_subscription(
        self, user_id: UUID, subscription_id: UUID
    ) -> User:
        """Назначает подписку пользователю."""
        user = await get_user_by_id(user_id, self.db)

        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=404, detail="Subscription not found"
            )

        if subscription in user.subscriptions:
            raise HTTPException(
                status_code=400, detail="User already subscribed"
            )

        user.subscriptions.append(subscription)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def remove_subscription(
            self, user_id: UUID, subscription_id: UUID
    ) -> User:
        """Отменяет подписку у пользователя."""
        user = await get_user_by_id(user_id, self.db)

        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription or subscription not in user.subscriptions:
            raise HTTPException(
                status_code=400, detail="User is not subscribed to this"
            )

        user.subscriptions.remove(subscription)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user_subscriptions(
            self, user_id: UUID
    ) -> list[Subscription]:
        """Возвращает список подписок пользователя."""
        user = await get_user_by_id(user_id, self.db)

        return user.subscriptions


@lru_cache()
def get_user_subscription_service(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> UserSubscriptionService:
    """
    Провайдер для получения экземпляра UserSubscriptionService.

    Функция создаёт синглтон экземпляр UserSubscriptionService, используя
    сессию Postgres, которая передаётся через Depends (зависимости FastAPI).

    :param db: Сессия Postgres, предоставленный через Depends.
    :return: Экземпляр UserSubscriptionService, который используется для
    работы с подписками пользователей.
    """
    logger.info(
        "Создаётся экземпляр UserSubscriptionService с использованием "
        "Postgres."
    )
    return UserSubscriptionService(db)
