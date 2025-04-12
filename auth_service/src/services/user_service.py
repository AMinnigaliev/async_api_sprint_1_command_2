import logging
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.core.security import (create_access_token, create_refresh_token,
                               verify_token)
from src.db.postgres import get_session
from src.db.redis_client import get_redis_auth
from src.models.user import User
from src.schemas.token import Token
from src.schemas.user import UserCreate, UserUpdate
from src.services.auth_service import AuthService
from typing import Annotated
from werkzeug.security import generate_password_hash
from src.schemas.token import Token

logger = logging.getLogger(__name__)


class UserService:

    """Сервис для работы с пользователями."""

    def __init__(self, db: AsyncSession, redis_client: AuthService):
        self.db = db
        self.redis_client = redis_client

    async def _create_tokens_from_user(self, user: User) -> tuple[str, str]:
        """
        Вспомогательный метод для создания access и refresh токенов и
        добавления refresh токена в Redis.
        """
        role = user.role.value

        access_token = create_access_token(user.id, role)
        refresh_token = create_refresh_token(user.id, role)

        await self.redis_client.set(
            refresh_token,
            settings.token_active,
            expire=int(timedelta(
                days=settings.refresh_token_expire_days).total_seconds()
            ),
        )

        return access_token, refresh_token

    async def create_user(self, user_data: UserCreate) -> User:
        if await User.get_user_by_login(self.db, user_data.login):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already registered",
            )

        new_user = User(
            login=user_data.login,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def login_user(self, login: str, password: str) -> Token:
        user = await User.get_user_by_login(self.db, login)
        if not user or not user.check_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        access_token, refresh_token = await self._create_tokens_from_user(user)
        await user.add_login_history(self.db)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def login_user_oauth(self, user: User) -> Token:
        """
        Авторизация OAuth-пользователя — создание токенов и запись истории входа.
        """
        access_token, refresh_token = await self._create_tokens_from_user(user)
        await user.add_login_history(self.db)
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_token: str) -> Token:
        user = await User.get_user_by_token(self.db, refresh_token)

        if not await self.redis_client.check_value(
            refresh_token, settings.token_active
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has revoked"
            )

        access_token, new_refresh_token = await self._create_tokens_from_user(
            user
        )

        await self.redis_client.delete(refresh_token)

        return Token(
            access_token=access_token, refresh_token=new_refresh_token
        )

    async def update_user(self, token: str, user_update: UserUpdate) -> User:
        user = await User.get_user_by_token(self.db, token)

        if await self.redis_client.check_value(
            token, settings.token_revoke
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has revoked"
            )

        if user_update.first_name:
            user.first_name = user_update.first_name
        if user_update.last_name:
            user.last_name = user_update.last_name
        if user_update.password:
            user.password = generate_password_hash(user_update.password)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def logout_user(self, access_token: str, refresh_token: str) -> None:
        if await self.redis_client.check_value(
            access_token, settings.token_revoke
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access-token has revoked"
            )

        access_payload = verify_token(access_token)
        del access_payload["exp"]
        refresh_payload = verify_token(refresh_token)
        del refresh_payload["exp"]

        if access_payload == refresh_payload:
            if self.redis_client.check_value(
                refresh_token, settings.token_active
            ):
                await self.redis_client.revoke_token(access_token)
                await self.redis_client.delete(refresh_token)
                return None

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh-token has revoked"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect refresh-token"
        )

    async def get_login_history(self, token: str, page_size: int, page_number: int) -> list:
        user = await User.get_user_by_token(self.db, token)

        if await self.redis_client.check_value(
            token, settings.token_revoke
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has revoked"
            )

        return await user.get_login_history(db=self.db, page_size=page_size, page_number=page_number)

    async def get_or_create_oauth_user(self, email: str, oauth_id: str, username: str) -> User:
        user = await User.get_user_by_email(self.db, email)
        if user:
            return user

        new_user = User(
            login=username,
            email=email,
            password=None,
            oauth_id=oauth_id
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

@lru_cache()
def get_user_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[AuthService, Depends(get_redis_auth)],
) -> UserService:
    """
    Провайдер для получения экземпляра UserService.
    """
    logger.info(
        "Создаётся экземпляр UserService с использованием "
        "Postgres и Redis."
    )
    return UserService(db, redis)
