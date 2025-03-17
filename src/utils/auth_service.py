import logging

from redis.asyncio import Redis

from src.core.config import settings
from src.core.exceptions import TokenServiceError
from src.utils.decorators import with_retry

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    @with_retry(settings.REDIS_EXCEPTIONS)
    async def is_revoke(self, token_key: str, log_info: str = "") -> bool:
        logger.debug(
            "Проверка access-токена в Redis: token_key=%s. %s",
            token_key, log_info
        )
        try:
            value = await self.redis_client.get(token_key)

        except settings.REDIS_EXCEPTIONS as e:
            logger.error(
                "Ошибка при проверке access-токена в Redis: "
                "token_key=%s, error=%s. %s",
                token_key, e, log_info
            )
            raise TokenServiceError(e)

        else:
            if value == settings.TOKEN_REVOKE:
                logger.info(
                    "Access-токен найден в списке недействительных: "
                    "token_key=%s. Доступ запрещён. %s",
                    token_key, log_info
                )
                return True

            logger.info(
                "Access-токен отсутствует в списке недействительных: "
                "token_key=%s. %s",
                token_key, log_info
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
