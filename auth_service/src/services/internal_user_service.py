import logging
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.db.redis_client import get_redis_auth
from src.models.user import User
from src.services.auth_service import AuthService


logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, db: AsyncSession, redis_client: AuthService):
        self.db = db
        self.redis_client = redis_client

    async def get_users_info(
        self,
        page_number: int,
        page_size: int,
        only_user: bool = True,
        user_ids: list[str] = None,
    ) -> dict[str, dict[str, Any] | list[User]]:
        stmt = select(User).where(User.is_active.is_(True))

        if only_user:
            stmt = stmt.where(User.role == "user")  # TODO: enum

        if user_ids:
            stmt = stmt.where(User.id.in_(user_ids))

        stmt = stmt.order_by(User.id)

        # Пагинация
        stmt_with_paginator = stmt.offset((page_number - 1) * page_size).limit(page_size)

        result_with_paginator = await self.db.execute(stmt_with_paginator)
        users: list[User] = result_with_paginator.scalars().all()

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = await self.db.scalar(count_stmt)

        response = {
            "meta": {
                "page": page_number,
                "page_size": page_size,
                "items_on_page": len(users),
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "users": users
        }

        return response


def get_user_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[AuthService, Depends(get_redis_auth)],
) -> UserService:
    return UserService(db, redis)
