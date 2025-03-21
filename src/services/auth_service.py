from datetime import UTC, datetime

from fastapi import Depends, HTTPException

from src.core.config import settings
from src.db.redis_client import get_redis_auth
from src.services.jwt_service import verify_token
from src.utils.auth_service import AuthService


async def check_token(
    token: str,
    required_roles: tuple[str],
    redis_client: AuthService = Depends(get_redis_auth)
) -> None:
    """
    Проверка валидности токена: подпись, срок действия и отсутствие в списке
    отозванных. Возвращает
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token)
    if await redis_client.is_revoke(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    if payload.get("role") not in required_roles:
        raise HTTPException(status_code=401, detail="No access rights")


async def revoke_token(
    token: str, redis_client: AuthService = Depends(get_redis_auth)
) -> None:
    """
    Отзыв токена: помещает его в Redis с TTL, равным
    оставшемуся времени жизни токена.
    """
    payload = verify_token(token)

    if exp := payload.get("exp"):
        ttl = int(exp - datetime.now(UTC).timestamp())

        if ttl > 0:
            await redis_client.set(token, settings.TOKEN_REVOKE, ttl)
