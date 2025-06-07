import aio_pika

from src.clients.rabbit import RabbitMQConnection


async def get_rabbit_channel() -> aio_pika.abc.AbstractChannel:
    return await RabbitMQConnection.get_channel()
