import logging.config

from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from src.core.config import settings
from src.core.exceptions import RedisUnavailable
from src.core.logger import LOGGING
from src.services.redis_service import RedisService

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

redis_url: RedisService | None = None


async def get_redis_url() -> RedisService:
    """
    Возвращает экземпляр ShortUrlService, обеспечивающий работу с Redis для
    коротких ссылок.
    """
    global redis_url

    try:
        if not redis_url or not await redis_url.redis_client.ping():
            logger.info("Создание клиента Redis для short_url...")

            redis_client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_short_url_db,
                decode_responses=True
            )
            if not await redis_client.ping():
                raise ConnectionError("Redis недоступен!")

            redis_url = RedisService(redis_client)

            logger.info("Клиент Redis для short_url успешно создан.")

    except settings.redis_exceptions as e:
        logger.error(f"Ошибка при создании клиента Redis для short_url: {e}")
        raise RedisUnavailable()

    return redis_url
