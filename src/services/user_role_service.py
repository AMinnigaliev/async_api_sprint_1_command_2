import logging
from functools import lru_cache
from http import HTTPStatus
from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.models.user import User, UserRoleEnum
from src.repositories.user import get_user_by_id

logger = logging.getLogger(__name__)


class UserRoleService:
    """Сервис для работы с ролями пользователей."""

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def assign_role(self, user_id: UUID, role: UserRoleEnum) -> User:
        """Назначает новую роль пользователю."""
        if role == UserRoleEnum.SUPERUSER:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Cannot assign superuser role",
            )

        user = await get_user_by_id(user_id, self.db)

        user.role = role
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user_role(self, user_id: UUID) -> str:
        """Возвращает роль пользователя в виде строки."""
        user = await get_user_by_id(user_id, self.db)

        return str(user.role)


@lru_cache()
def get_user_role_service(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> UserRoleService:
    """
    Провайдер для получения экземпляра UserRoleService.

    Функция создаёт синглтон экземпляр UserRoleService, используя
    сессию Postgres, которая передаётся через Depends (зависимости FastAPI).

    :param db: Сессия Postgres, предоставленный через Depends.
    :return: Экземпляр UserRoleService, который используется для
    работы с подписками пользователей.
    """
    logger.info(
        "Создаётся экземпляр UserRoleService с использованием "
        "Postgres."
    )
    return UserRoleService(db)
