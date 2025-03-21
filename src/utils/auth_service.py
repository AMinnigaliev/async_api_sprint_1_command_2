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
        """Проверяет, является ли токен недействительным (отозванным)."""
        logger.debug(
            "Проверка токена в Redis: token_key=%s. %s",
            token_key, log_info
        )
        try:
            value = await self.redis_client.get(token_key)

        except settings.REDIS_EXCEPTIONS as e:
            logger.error(
                "Ошибка при проверке токена в Redis: "
                "token_key=%s, error=%s. %s",
                token_key, e, log_info
            )
            raise TokenServiceError(e)

        if value == settings.TOKEN_REVOKE:
            logger.info(
                "Токен найден в списке недействительных: token_key=%s. %s",
                token_key, log_info
            )
            return True

        logger.info(
            "Токен отсутствует в списке недействительных: token_key=%s. %s",
            token_key, log_info
        )
        return False

    @with_retry(settings.REDIS_EXCEPTIONS)
    async def set(
        self, token_key: str, value: bytes, expire: int, log_info: str = ""
    ) -> None:
        """Добавляет токен в Redis с временем жизни."""
        logger.debug(
            "Добавление токена в Redis: token_key=%s, expire=%d сек. %s",
            token_key, expire, log_info
        )
        try:
            await self.redis_client.set(token_key, value, ex=expire)

        except settings.REDIS_EXCEPTIONS as e:
            logger.error(
                "Ошибка при добавлении токена в Redis: token_key=%s, error=%s. %s",
                token_key, e, log_info
            )
            raise TokenServiceError(e)

        logger.info(
            "Токен добавлен в Redis: token_key=%s, expire=%d сек. %s",
            token_key, expire, log_info
        )

    @with_retry(settings.REDIS_EXCEPTIONS)
    async def delete(self, refresh_token: str, log_info: str = "") -> None:
        """Удаляет refresh-токен и помечает access-токен как отозванный."""
        logger.debug(
            "Удаление refresh-токена и отзыв access-токена: token_key=%s. %s",
            refresh_token, log_info
        )
        try:
            # Удаляем refresh-токен
            await self.redis_client.delete(refresh_token)

            # Отзываем access-токен
            await self.redis_client.set(
                refresh_token, settings.TOKEN_REVOKE,
                ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

        except settings.REDIS_EXCEPTIONS as e:
            logger.error(
                "Ошибка при удалении refresh-токена в Redis: "
                "token_key=%s, error=%s. %s",
                refresh_token, e, log_info
            )
            raise TokenServiceError(e)

        logger.info(
            "Refresh-токен удалён, access-токен отозван: token_key=%s. %s",
            refresh_token, log_info
        )

    async def close(self):
        """Закрывает соединение с Redis."""
        logger.info("Закрытие соединения с Redis...")

        try:
            await self.redis_client.close()
            logger.info("Соединение с Redis успешно закрыто.")

        except (settings.REDIS_EXCEPTIONS, RuntimeError) as e:
            logger.error("Ошибка при закрытии соединения с Redis: %s", e)
            raise TokenServiceError(e)
