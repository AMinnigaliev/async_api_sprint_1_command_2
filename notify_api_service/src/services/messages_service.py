import logging.config
from functools import lru_cache

import aio_pika
from fastapi import Depends, HTTPException, status

from src.clients.get_rabbit_channel import get_rabbit_channel
from src.core.config import settings
from src.core.logger import LOGGING
from src.schemas.message import EnrichedMessage, IncomingMessage

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class MessagesService:
    """Сервис для работы с сообщениями системы оповещения."""

    def __init__(self, rabbit_channel: aio_pika.abc.AbstractChannel) -> None:
        self.rabbit_channel = rabbit_channel

    async def accept_message(self, request_id: str, message: IncomingMessage):
        """Добавить сообщение в RabbitMQ."""
        task_id = message.id
        logger.info("Обработка полученного оповещения. task_id=%s", task_id)

        data = message.model_dump()
        data["kwargs"]["meta"]["X-Request-Id"] = request_id
        enriched_data = EnrichedMessage.model_validate(data)

        try:
            rabbit_msg = aio_pika.Message(
                body=enriched_data.model_dump_json(
                    by_alias=True
                ).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await self.rabbit_channel.default_exchange.publish(
                rabbit_msg,
                routing_key="default"
            )

            logger.info(
                "Сообщение успешно поставлено в очередь. task_id=%s", task_id
            )

        except settings.rabbit_exceptions as exc:

            logger.error(
                "Не удалось отправить сообщение в RabbitMQ. "
                "task_id=%s error=%s",
                task_id, exc
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to publish message to RabbitMQ",
            )

        except Exception as exc:
            logger.error(
                "Неожиданная ошибка при отправке сообщения в RabbitMQ. "
                "task_id=%s error=%s",
                task_id, exc
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error while processing notification.",
            )


@lru_cache()
def get_messages_service(
    rabbit_channel=Depends(get_rabbit_channel)
) -> MessagesService:
    """
    Провайдер для получения экземпляра MessagesService.

    Функция создаёт экземпляр MessagesService, используя rabbit_channel,
    который передаётся через Depends (зависимости FastAPI).
    """
    logger.info(
        "Создаётся экземпляр MessagesService с использованием RabbitMQ."
    )
    return MessagesService(rabbit_channel)
