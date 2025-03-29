from datetime import datetime, timedelta, UTC
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from src.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    user_id: str | UUID,
    role: str,
    subscriptions: list[str],
    expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, Any] = {
        "user_id": str(user_id),
        "role": role,
        "subscriptions": subscriptions,
        "exp": datetime.now(UTC) + (expires_delta or timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )),
    }
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def create_refresh_token(
    user_id: str | UUID,
    role: str,
    subscriptions: list[str],
    expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, Any] = {
        "user_id": str(user_id),
        "role": role,
        "subscriptions": subscriptions,
        "exp": datetime.now(UTC) + (expires_delta or timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )),
    }
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def verify_token(token: str) -> dict:
    """Проверяет валидность JWT-токена."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
