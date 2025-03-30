import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.models.subscription import Subscription
from src.schemas.subscription import SubscriptionCreateUpdate

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Сервис для работы с подписками."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_subscriptions(self) -> list[Subscription]:
        """Возвращает список всех подписок."""
        await self.db.execute(select(Subscription))

    async def create_subscription(
        self, create_data: SubscriptionCreateUpdate
    ) -> Subscription:
        """Создаёт новую подписку."""
        subscription = Subscription(**create_data.model_dump())

        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def subscription_update(
        self, subscription_id: UUID, update_data: SubscriptionCreateUpdate
    ) -> Subscription:
        """Изменяет существующую подписку."""
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=404, detail="Subscription not found"
            )

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(subscription, key, value)

        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def delete_subscription(
        self, subscription_id: UUID
    ) -> dict:
        """Удаляет существующую подписку."""
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=404, detail="Subscription not found"
            )

        await self.db.delete(subscription)
        await self.db.commit()

        return {"message": "Subscription deleted"}


@lru_cache()
def get_subscription_service(
        db: Annotated[AsyncSession, Depends(get_session)],
) -> SubscriptionService:
    """
    Провайдер для получения экземпляра SubscriptionService.

    Функция создаёт синглтон экземпляр SubscriptionService, используя
    сессию Postgres, которая передаётся через Depends (зависимости FastAPI).

    :param db: Сессия Postgres, предоставленный через Depends.
    :return: Экземпляр SubscriptionService, который используется для
    работы с подписками пользователей.
    """
    logger.info(
        "Создаётся экземпляр SubscriptionService с использованием "
        "Postgres."
    )
    return SubscriptionService(db)
