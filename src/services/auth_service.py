import logging
from datetime import UTC, datetime

from redis.asyncio import Redis

from src.core.config import settings
from src.core.exceptions import TokenServiceError
from src.services.jwt_service import verify_token
from src.utils.decorators import with_retry

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    @with_retry(settings.REDIS_EXCEPTIONS)
    async def check_value(
        self, token_key: str, value: bytes, log_info: str = ""
    ) -> bool:
        logger.debug(
            "Проверка токена в Redis: token_key=%s, check_value=%s. %s",
            token_key, value, log_info
        )
        try:
            redis_value = await self.redis_client.get(token_key)

        except settings.REDIS_EXCEPTIONS as e:
            logger.error(
                "Ошибка при проверке токена в Redis: "
                "token_key=%s, check_value=%s, error=%s. %s",
                token_key, value, e, log_info
            )
            raise TokenServiceError(e)

        if redis_value == value:
            logger.info(
                "Токен найден в списке '%s': token_key=%s. %s",
                value.decode(), token_key, log_info
            )
            return True

        logger.info(
            "Токен отсутствует в списке '%s': "
            "token_key=%s. %s",
            value.decode(), token_key, log_info
        )
        return False

    @with_retry(settings.REDIS_EXCEPTIONS)
    async def set(
        self, token_key: str, value: bytes, expire: int, log_info: str = ""
    ) -> None:
        logger.debug(
            "Добавление access-токена в список недействительных: "
            "token_key=%s, expire=%d сек. %s",
            token_key, value, expire, log_info
        )
        try:
            await self.redis_client.set(token_key, value, ex=expire)

        except settings.REDIS_EXCEPTIONS as e:
            logger.error(
                "Ошибка при добавлении access-токена в Redis: "
                "token_key=%s, error=%s. %s",
                token_key, value, e, log_info
            )
            raise TokenServiceError(e)

        else:
            logger.info(
                "Access-токен добавлен в список недействительных: "
                "token_key=%s, expire=%d сек. %s",
                token_key, expire, log_info
            )

    async def revoke_token(self, token: str) -> None:
        """
        Отзыв токена: помещает его в Redis с TTL, равным
        оставшемуся времени жизни токена.
        """
        payload = verify_token(token)

        if exp := payload.get("exp"):
            ttl = int(exp - datetime.now(UTC).timestamp())

            if ttl > 0:
                await self.set(token, settings.TOKEN_REVOKE, ttl)

    async def close(self):
        logger.info("Закрытие соединения с Redis по работе с access-токен...")

        try:
            await self.redis_client.close()
            logger.info(
                "Соединение с Redis по работе с access-токен успешно закрыто."
            )

        except (settings.REDIS_EXCEPTIONS, RuntimeError) as e:
            logger.error(
                "Ошибка при закрытии соединения с Redis по работе с "
                "access-токен: %s", e
            )
            raise TokenServiceError(e)
