import logging

from redis.asyncio import Redis

from src.core.config import settings
from src.utils.auth_service import AuthService
from src.utils.cache_service import CacheService

logger = logging.getLogger(__name__)

redis_cache: CacheService | None = None
redis_auth: AuthService | None = None


async def create_redis_client(db: int) -> Redis:
    """Создание и проверка клиента Redis."""
    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=db,
    )
    if not await redis_client.ping():
        raise ConnectionError("Redis недоступен!")
    return redis_client


async def get_redis_auth() -> AuthService:
    """Получить или создать Redis клиента для Auth."""
    global redis_auth
    if not redis_auth or not await redis_auth.redis_client.ping():
        logger.info("Создание клиента Redis для auth...")
        try:
            redis_client = await create_redis_client(db=0)
            redis_auth = AuthService(redis_client)
            logger.info("Клиент Redis для auth успешно создан.")
        except Exception as e:
            logger.error("Ошибка при создании клиента Redis для auth: %s", e)
            raise
    return redis_auth


async def get_redis_cache() -> CacheService:
    """Получить или создать Redis клиента для кеша."""
    global redis_cache
    if not redis_cache or not await redis_cache.redis_client.ping():
        logger.info("Создание клиента Redis для кеша...")
        try:
            redis_client = await create_redis_client(db=1)
            redis_cache = CacheService(redis_client)
            logger.info("Клиент Redis для кеша успешно создан.")
        except Exception as e:
            logger.error("Ошибка при создании клиента Redis для кеша: %s", e)
            raise
    return redis_cache
