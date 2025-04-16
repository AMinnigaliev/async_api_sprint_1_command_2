import logging

from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from src.core.config import settings
from src.utils.cache_service import CacheService

logger = logging.getLogger(__name__)

redis_cache: CacheService | None = None


async def get_redis_cache() -> CacheService:
    """
    Возвращает экземпляр CacheService, обеспечивающий работу с Redis для
    кэширования.
    """
    global redis_cache

    try:
        if not redis_cache or not await redis_cache.redis_client.ping():
            logger.info("Создание клиента Redis для кеша...")
            redis_client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=1,
            )
            if not await redis_client.ping():
                raise ConnectionError("Redis недоступен!")

            redis_cache = CacheService(redis_client)

            logger.info("Клиент Redis для кеша успешно создан.")

    except Exception as e:
        logger.error(f"Ошибка при создании клиента Redis для кеша: {e}")
        raise

    return redis_cache
