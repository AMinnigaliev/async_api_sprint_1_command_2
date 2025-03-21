from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt

from src.core.config import settings


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Создание access-токена с заданным временем жизни."""
    to_encode = data.copy()

    expire = datetime.now(UTC) + (expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ))
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def create_refresh_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Создание refresh-токена с заданным временем жизни."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    ))
    to_encode.update({"exp": expire})

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
