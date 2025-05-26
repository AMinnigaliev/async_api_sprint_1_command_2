import logging.config

from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError

from src.core.config import settings
from src.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

_mongo_client: AsyncMongoClient | None = None


async def get_mongo_client() -> AsyncMongoClient:
    """
    Возвращает экземпляр AsyncMongoClient, обеспечивающий работу с MongoDB.
    """
    global _mongo_client

    logger.info("Проверка существующего клиента MongoDB...")

    if _mongo_client is not None:

        logger.info("Пинг существующего клиента MongoDB...")

        try:
            await _mongo_client.admin.command("ping")

            logger.info("Существующий клиент MongoDB прошёл проверки.")

            return _mongo_client

        except ServerSelectionTimeoutError:

            logger.info(
                "Существующий клиент MongoDB не отвечает. Закрываем "
                "соединение..."
            )

            await _mongo_client.close()
            _mongo_client = None

    logger.info("Создание клиента MongoDB...")

    _mongo_client = AsyncMongoClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
        maxPoolSize=settings.mongo_max_pool_size,
    )
    await _mongo_client.admin.command("ping")

    logger.info("Клиент MongoDB успешно создан.")

    return _mongo_client
