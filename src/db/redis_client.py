import logging

from redis.asyncio import Redis

from src.core.config import settings
from src.services.auth_service import AuthService
from src.utils.cache_service import CacheService

logger = logging.getLogger(__name__)

redis_auth: AuthService | None = None
redis_cache: CacheService | None = None


async def get_redis(
    redis: AuthService | CacheService,
) -> AuthService | CacheService:
    """
    Проверяет доступность переданного Redis-клиента и создаёт новый, если он
    недоступен.
    """
    # Проверка, существует ли redis и активно ли соединение
    if not redis or not await redis.redis_client.ping():
        logger.info("Создание клиента %s", redis.__class__.__name__)
        try:
            redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=redis.db,
            )
            if not await redis_client.ping():
                raise ConnectionError("Redis недоступен!")

            redis = redis.__class__(redis_client)

            logger.info("Клиент %s успешно создан.", redis.__class__.__name__)

        except Exception as e:
            logger.error(
                "Ошибка при создании клиента %s: %s",
                redis.__class__.__name__, e
            )
            raise

    return redis


async def get_redis_auth() -> AuthService:
    """
    Возвращает экземпляр AuthService, обеспечивающий работу с Redis для
    аутентификации.
    """
    global redis_auth
    return await get_redis(redis_auth)


async def get_redis_cache() -> CacheService:
    """
    Возвращает экземпляр CacheService, обеспечивающий работу с Redis для
    кэширования.
    """
    global redis_cache
    return await get_redis(redis_cache)
