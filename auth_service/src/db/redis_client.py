import logging

from redis.asyncio import Redis

from src.core.config import settings
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)

redis_auth: AuthService | None = None


async def get_redis_auth() -> AuthService:
    """
    Возвращает экземпляр AuthService, обеспечивающий работу с Redis для
    аутентификации.
    """
    global redis_auth

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

            redis_auth = AuthService(redis_client)

            logger.info("Клиент Redis для auth успешно создан.")

        except Exception as e:
            logger.error(f"Ошибка при создании клиента Redis для auth: {e}")
            raise

    return redis_auth
