import base64
import hashlib
import logging.config
from functools import lru_cache

from fastapi import Depends, HTTPException, status

from src.core.config import settings
from src.core.logger import LOGGING
from src.db.redis_client import get_redis_url
from src.schemas.url import ShortUrl
from src.services.redis_service import RedisService

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class ShortUrlService:
    """Сервис для работы с короткими ссылками."""

    def __init__(self, redis_url: RedisService) -> None:
        self.redis_url = redis_url

    @staticmethod
    def _generate_code(url: str, length: int = settings.code_length) -> str:
        """
        Метод для получения кода на основе переданного url.
        """
        sha = hashlib.sha256(url.encode()).digest()
        # Кодируем хэш в base64, убираем спецсимволы, обрезаем
        code = base64.urlsafe_b64encode(sha).decode()[:length]
        return code

    async def create(self, url: str) -> ShortUrl:
        """Добавить url в базу коротких ссылок."""
        code = self._generate_code(url)

        if not await self.redis_url.get(code):
            await self.redis_url.set(code, url)

        short_url = f"http://{settings.domain}/{code}"

        return ShortUrl(short_url=short_url)

    async def get_url(self, code: str) -> str:
        """Получить url из базы коротких ссылок."""
        url = await self.redis_url.get(code)
        if not url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short URL not found",
            )
        return url.url


@lru_cache()
def get_short_url_service(
    redis_url=Depends(get_redis_url)
) -> ShortUrlService:
    """
    Провайдер для получения экземпляра ShortUrlService.

    Функция создаёт экземпляр ShortUrlService, используя redis_url,
    который передаётся через Depends (зависимости FastAPI).
    """
    logger.info(
        "Создаётся экземпляр ShortUrlService с использованием Redis."
    )
    return ShortUrlService(redis_url)
