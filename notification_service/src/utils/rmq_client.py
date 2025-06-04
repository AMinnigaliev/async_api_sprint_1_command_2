from aio_pika import connect, Message, ExchangeType
from aio_pika.abc import AbstractIncomingMessage
from typing import Optional, Callable, Awaitable


class AsyncRabbitMQClient:
    DEF_HEADERS = {
        "Content-Type": "application/json",
        "Message-Format": "html-with-metadata"
    }

    def __init__(
        self,
        amqp_url: str,
        queue_name: str,
        exchange_name: str = "",
        exchange_type: ExchangeType = ExchangeType.DIRECT,
        routing_key: str = "",
    ):
        """
        Инициализация клиента RabbitMQ.

        :param amqp_url: URL для подключения к RabbitMQ (например, 'amqp://guest:guest@localhost/')
        :param queue_name: Имя очереди
        :param exchange_name: Имя exchange (по умолчанию - прямой exchange)
        :param exchange_type: Тип exchange (по умолчанию DIRECT)
        :param routing_key: Ключ маршрутизации
        """
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key or queue_name
        self.connection = None
        self.channel = None
        self.queue = None
        self.exchange = None

    async def connect(self) -> None:
        """Установка соединения с RabbitMQ и создание канала."""
        self.connection = await connect(self.amqp_url)
        self.channel = await self.connection.channel()

        # Объявляем exchange, если указано имя
        if self.exchange_name:
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                self.exchange_type,
                durable=True
            )

        # Объявляем очередь
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True
        )

        # Привязываем очередь к exchange, если exchange указан
        if self.exchange_name:
            await self.queue.bind(self.exchange, self.routing_key)

    async def disconnect(self) -> None:
        """Закрытие соединения с RabbitMQ."""
        if self.connection:
            await self.connection.close()

    async def publish(self, message_body: str, headers: Optional[dict] = None) -> None:
        """
        Публикация сообщения в RabbitMQ.

        :param message_body: Тело сообщения
        :param headers: Заголовки сообщения (опционально)
        """
        if not self.connection:
            await self.connect()

        message = Message(
            body=message_body.encode(),
            headers=headers or {},
            delivery_mode=2  # Сообщение будет сохранено на диск
        )

        if self.exchange:
            await self.exchange.publish(message, routing_key=self.routing_key)
        else:
            await self.channel.default_exchange.publish(message, routing_key=self.queue_name)

    async def consume(
            self,
            callback: Callable[[AbstractIncomingMessage], Awaitable[None]],
            prefetch_count: int = 1
    ) -> None:
        """
        Начать потребление сообщений из очереди.

        :param callback: Асинхронная функция для обработки сообщений
        :param prefetch_count: Максимальное количество неподтвержденных сообщений
        """
        if not self.connection:
            await self.connect()

        # Устанавливаем лимит неподтвержденных сообщений
        await self.channel.set_qos(prefetch_count=prefetch_count)

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Ошибка при обработке сообщения: {e}")
                    # Отказываемся от сообщения и помещаем его обратно в очередь
                    await message.nack(requeue=True)
                else:
                    # Подтверждаем обработку сообщения
                    await message.ack()
