from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from jose import jwt, JWTError

from src.models.user import User
from src.schemas.user import UserCreate, Token, UserUpdate
from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
)
from src.services.auth_service import AuthService


class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
        existing_user = await User.get_user_by_login(db, user_data.login)
        if existing_user:
            raise HTTPException(status_code=400, detail="Login already registered")

        new_user = User(
            login=user_data.login,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def login_user(login: str, password: str, db: AsyncSession, auth_service: AuthService) -> Token:
        user = await User.get_user_by_login(db, login)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect login or password")

        role = user.role.value
        subscriptions = [s.name for s in user.subscriptions]

        access_token = create_access_token(
            user.id, role, subscriptions,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            user.id, role, subscriptions,
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        await auth_service.set(
            refresh_token,
            settings.TOKEN_ACTIVE,
            expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        await user.add_login_history(db)

        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def refresh_tokens(refresh_token: str, auth_service: AuthService) -> Token:
        is_valid = await auth_service.check_value(refresh_token, settings.TOKEN_ACTIVE)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or revoked")

        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("user_id")
            role = payload.get("role")
            subscriptions = payload.get("subscriptions", [])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        access_token = create_access_token(
            user_id, role, subscriptions,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        new_refresh_token = create_refresh_token(
            user_id, role, subscriptions,
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        await auth_service.set(
            new_refresh_token,
            settings.TOKEN_ACTIVE,
            expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return Token(access_token=access_token, refresh_token=new_refresh_token)

    @staticmethod
    async def logout_user(access_token: str, refresh_token: str, auth_service: AuthService) -> None:
        await auth_service.delete(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def update_user(user: User, user_update: UserUpdate, db: AsyncSession) -> User:
        if user_update.login:
            user.login = user_update.login
        if user_update.password:
            user.password = get_password_hash(user_update.password)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_login_history(user: User) -> list:
        return await user.get_login_history()
