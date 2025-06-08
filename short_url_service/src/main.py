import logging.config

from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.api.v1 import healthcheck, redirect, short_url
from src.clients.rabbit import RabbitMQConnection
from src.core.config import settings
from src.core.logger import LOGGING
from src.db.redis_client import get_redis_url
from src.dependencies import check_request_id

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/short_url/openapi',
    openapi_url='/api/v1/short_url/openapi.json',
    default_response_class=ORJSONResponse,
    dependencies=[
        Depends(check_request_id),
    ]
)
FastAPIInstrumentor.instrument_app(app)
api_router = APIRouter()


@app.on_event('startup')
async def startup():
    """
    Событие запуска приложения: нициализация подключение к Redis.
    """
    # Инициализация подключения к Redis
    logger.info("Инициализация подключений к Redis...")
    try:
        redis_url = await get_redis_url()

        # Проверяем доступность Redis
        if not await redis_url.redis_client.ping():
            raise ConnectionError("Redis не отвечает на запросы.")

    except settings.redis_exceptions as e:
        logger.error("Ошибка подключения к Redis: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Redis. Приложение завершает работу."
        )

    else:
        logger.info("Подключение к Redis успешно установлено.")

    logger.info("Все подключения успешно установлены.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие завершения работы приложения: закрытие подключений к Redis.
    """
    # Закрытие подключений к Redis
    redis_url = await get_redis_url()
    if redis_url:
        await redis_url.close()


# Подключение роутеров
api_router.include_router(
    short_url.router, prefix="/api/v1/short_url/create", tags=["short_url"]
)
api_router.include_router(
    healthcheck.router, prefix="/api/v1/short_url", tags=["healthcheck"]
)
api_router.include_router(
    redirect.router, prefix="/short_url", tags=["redirect"]
)

app.include_router(api_router)
