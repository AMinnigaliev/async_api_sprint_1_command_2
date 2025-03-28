from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    user_id: str,
    role: str,
    subscriptions: list[str],
    expires_delta: timedelta
) -> str:
    to_encode: dict[str, Any] = {
        "user_id": user_id,
        "role": role,
        "subscriptions": subscriptions,
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    user_id: str,
    role: str,
    subscriptions: list[str],
    expires_delta: timedelta
) -> str:
    to_encode: dict[str, Any] = {
        "user_id": user_id,
        "role": role,
        "subscriptions": subscriptions,
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
