import logging

from pydantic import ValidationError
from redis.asyncio import Redis

from src.core.config import settings
from src.core.exceptions import RedisUnavailable
from src.schemas.url import FullUrl

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get(self, code: str) -> FullUrl | None:
        """Получает полную ссылку по коду."""
        logger.debug("Получение полной ссылки из Redis: code=%s.", code)
        try:
            url = await self.redis_client.get(code)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка получении ссылки из Redis: code=%s, error=%s.", code, e
            )
            raise RedisUnavailable()

        if url:
            logger.info("Ссылка найден в Redis: code=%s. url=%s.", code, url)

            try:
                return FullUrl(url=url)

            except ValidationError as e:
                logger.warning(
                    "Ошибка при валидации ссылки из Redis в модель %s: %s. "
                    "Данные для валидации: %s",
                    FullUrl.__name__, e, url
                )
                await self.delete(code)

                return None

        return None

    async def set(
        self, code: str, url: str, expire: int = settings.short_url_expire
    ) -> None:
        """Добавляет ссылку в Redis с временем жизни."""
        logger.debug(
            "Добавление ссылки в Redis: code=%s, url=%s, expire=%d сек.",
            code, url, expire,
        )
        try:
            await self.redis_client.set(code, url, ex=expire)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка при добавлении ссылки в Redis: code=%s, error=%s.",
                code, e
            )
            raise RedisUnavailable()

        logger.info(
            "Ссылка добавлена в Redis: code=%s, expire=%d сек.", code, expire
        )

    async def delete(self, code: str) -> None:
        """Удаляет ссылку из Redis."""
        logger.debug("Удаление ссылки: code=%s", code)

        try:
            await self.redis_client.delete(code)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка при удалении токена: code=%s, error=%s", code, e
            )
            raise RedisUnavailable()

        logger.info("Ссылка удалена: code=%s", code)

    async def close(self):
        """Закрывает соединение с Redis."""
        logger.info("Закрытие соединения с Redis...")
        try:
            await self.redis_client.close()
            logger.info("Соединение с Redis успешно закрыто.")

        except (settings.redis_exceptions, RuntimeError) as e:
            logger.error(
                "Ошибка при закрытии соединения с Redis: %s", e
            )
