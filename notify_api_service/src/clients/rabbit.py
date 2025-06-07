import asyncio
import logging.config

import aio_pika

from src.core.config import settings
from src.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class RabbitMQConnection:
    _connection: aio_pika.RobustConnection | None = None
    _channel: aio_pika.abc.AbstractChannel | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_connection(cls) -> aio_pika.RobustConnection:
        """
        Возвращает singleton-подключение к RabbitMQ. Если подключение не
        создано или закрыто — создаёт его единожды.
        """
        if cls._connection and not cls._connection.is_closed:
            return cls._connection

        async with cls._lock:
            if cls._connection is None or cls._connection.is_closed:
                logger.info(
                    "Попытка подключения к RabbitMQ к %s",
                    settings.rabbit_url
                )
                try:
                    cls._connection = await aio_pika.connect_robust(
                        settings.rabbit_url
                    )
                    logger.info("Успешное подключение к RabbitMQ")

                except aio_pika.exceptions.AMQPConnectionError as e:
                    logger.error(
                        "Не удалось подключиться к RabbitMQ: %s", e
                    )
                    raise

                except Exception as e:
                    logger.exception(
                        "Неожиданная ошибка при подключении к RabbitMQ: %s", e
                    )
                    raise

        return cls._connection

    @classmethod
    async def get_channel(cls) -> aio_pika.abc.AbstractChannel:
        """
        Возвращает singleton-канал. Если канал не создан или закрыт —
        создаёт его единожды.
        """
        connection = await cls.get_connection()

        if cls._channel and not cls._channel.is_closed:
            return cls._channel

        async with cls._lock:
            if cls._channel is None or cls._channel.is_closed:
                logger.info(
                    "Попытка открыть новый канал в соединении RabbitMQ"
                )
                try:
                    cls._channel = await connection.channel(
                        publisher_confirms=True
                    )
                    logger.info("Канал RabbitMQ успешно открыт")

                except aio_pika.exceptions.ChannelClosed as e:
                    logger.error("Канал был неожиданно закрыт: %s", e)
                    raise

                except Exception as e:
                    logger.exception(
                        "Неожиданная ошибка при открытии канала RabbitMQ %s", e
                    )
                    raise

        return cls._channel

    @classmethod
    async def close(cls):
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            cls._connection = None
