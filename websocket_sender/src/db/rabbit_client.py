import json
import logging
from aio_pika import connect_robust, IncomingMessage
from src.core.config import settings
from src.services.connection_manager import push_to_user
from src.schemas.notification import DeliveryMessage

logger = logging.getLogger(__name__)


class RabbitClient:
    """Слушает фиксированную очередь `websocket` и раздаёт сообщения по сокетам."""

    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    async def start(self):
        self.connection = await connect_robust(settings.amqp_url)
        self.channel = await self.connection.channel()

        # очередь создаёт notification-service; мы только подписываемся
        queue = await self.channel.declare_queue(
            name=settings.websocket_queue,
            durable=True,
        )
        await queue.consume(self.handle_message, no_ack=False)
        logger.info("✅ Listening queue %s", settings.websocket_queue)

    async def handle_message(self, message: IncomingMessage):
        async with message.process():
            try:
                delivery = DeliveryMessage.model_validate_json(message.body)
            except Exception as err:
                logger.exception("💥 Invalid message: %s", err)
                return

            for user_id, body in delivery.message_body.items():
                # body может быть HTML-строкой или dict (json payload) — приводим к строке
                if not isinstance(body, str):
                    body = json.dumps(body, ensure_ascii=False)
                await push_to_user(user_id, body)
