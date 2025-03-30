from datetime import datetime, timedelta, UTC
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jose import jwt, ExpiredSignatureError, JWTError

from src.core.config import settings


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
        # Список обязательных полей, которые должен содержать токен
        required_fields = ["user_id", "role", "subscriptions", "exp"]

        for field in required_fields:
            if field not in payload:
                raise JWTError

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
