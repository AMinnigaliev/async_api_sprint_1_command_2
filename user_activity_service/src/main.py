import logging

from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.api.v1 import bookmark, film_rating, film_review, healthcheck
from src.core.config import settings
from src.db.mongo_client import get_mongo_client
from src.db.redis_client import get_redis_cache
from src.dependencies import check_request_id
from src.middleware import AsyncRateLimitMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/activity/openapi',
    openapi_url='/api/v1/activity/openapi.json',
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
    Событие запуска приложения: подключений к Redis и MongoDB.
    """
    # Инициализация подключения к Redis
    logger.info("Инициализация подключения к Redis...")
    try:
        redis_cache = await get_redis_cache()

        # Проверяем доступность Redis-кеш
        if not await redis_cache.redis_client.ping():
            raise ConnectionError("Redis-кеш не отвечает на запросы.")

    except settings.redis_exceptions as e:
        logger.error("Ошибка подключения к Redis: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Redis. Приложение завершает работу."
        )

    else:
        logger.info("Подключение к Redis успешно установлено.")

    # Инициализация подключения к MongoDB
    logger.info("Инициализация подключения к MongoDB...")
    try:
        await get_mongo_client()

    except settings.mongo_exceptions as e:
        logger.error("Ошибка подключения к MongoDB: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к MongoDB. Приложение завершает работу."
        )

    else:
        logger.info("Подключение к MongoDB успешно установлено.")

    logger.info("Все подключения успешно установлены.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие завершения работы приложения: закрытие подключений к Redis и
    MongoDB.
    """
    # Закрытие подключения к Redis
    redis_cache = await get_redis_cache()
    if redis_cache:
        await redis_cache.close()

    # Закрытие подключения к MongoDB
    mongo_client = await get_mongo_client()
    if mongo_client:
        await mongo_client.close()


# Подключение роутеров
api_router.include_router(
    bookmark.router, prefix="/user-activity/bookmarks", tags=["bookmarks"]
)
api_router.include_router(
    film_rating.router, prefix="/user-activity/ratings", tags=["ratings"]
)
api_router.include_router(
    film_review.router, prefix="/user-activity/reviews", tags=["reviews"]
)
api_router.include_router(
    healthcheck.router, prefix="/user-activity", tags=["healthcheck"]
)

app.include_router(api_router)

# Middleware:
app.add_middleware(AsyncRateLimitMiddleware)
