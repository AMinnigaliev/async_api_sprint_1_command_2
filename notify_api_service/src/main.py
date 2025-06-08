import logging.config

from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.api.v1 import healthcheck, messages
from src.clients.rabbit import RabbitMQConnection
from src.core.config import settings
from src.core.logger import LOGGING
from src.dependencies import check_request_id

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/notify_api/openapi',
    openapi_url='/api/v1/notify_api/openapi.json',
    default_response_class=ORJSONResponse,
    dependencies=[
        Depends(check_request_id),
    ]
)
FastAPIInstrumentor.instrument_app(app)
api_router = APIRouter(prefix="/api/v1")


@app.on_event('startup')
async def startup():
    """
    Событие запуска приложения: соединения к RabbitMQ.
    """
    # Создание соединения к RabbitMQ
    logger.info("Создание соединения с RabbitMQ...")

    channel = await RabbitMQConnection.get_channel()
    # Гарантируем, что очередь "default" существует:
    await channel.declare_queue("default", durable=True)

    logger.info("Соединение с RabbitMQ успешно установлено.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие завершения работы приложения: закрытие соединения с RabbitMQ.
    """
    # Закрытие соединения к RabbitMQ
    await RabbitMQConnection.close()


# Подключение роутеров
api_router.include_router(
    messages.router, prefix="/notify_api/messages", tags=["messages"]
)
api_router.include_router(
    healthcheck.router, prefix="/notify_api", tags=["healthcheck"]
)

app.include_router(api_router)
