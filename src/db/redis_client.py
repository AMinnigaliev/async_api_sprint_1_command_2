import logging

from redis.asyncio import Redis

from src.core.config import Settings
from src.utils.auth_service import AuthService
from src.utils.cache_service import CacheService

logger = logging.getLogger(__name__)

settings = Settings()

redis_cache: CacheService | None = None
redis_auth: AuthService | None = None


async def get_redis_auth() -> CacheService:
    global redis_auth
    # Проверка, существует ли redis_auth и активно ли соединение
    if not redis_auth or not await redis_auth.redis_client.ping():
        logger.info("Создание клиента Redis для auth...")
        try:
            redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=0,
            )
            if not await redis_client.ping():
                raise ConnectionError("Redis недоступен!")

            redis_auth = CacheService(redis_client)

            logger.info("Клиент Redis для auth успешно создан.")

        except Exception as e:
            logger.error(f"Ошибка при создании клиента Redis для auth: {e}")
            raise

    return redis_auth


async def get_redis_cache() -> CacheService:
    global redis_cache
    # Проверка, существует ли redis_cache и активно ли соединение
    if not redis_cache or not await redis_cache.redis_client.ping():
        logger.info("Создание клиента Redis для кеша...")
        try:
            redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
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
