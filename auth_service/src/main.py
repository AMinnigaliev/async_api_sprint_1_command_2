import logging

from sqlalchemy import text
from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.api.v1 import healthcheck, user, user_role
from src.core.config import settings
from src.db.postgres import async_session
from src.db.redis_client import get_redis_auth
from src.dependencies import check_request_id
from src.middleware import AsyncRateLimitMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/auth/openapi',
    openapi_url='/api/auth/openapi.json',
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
    Событие запуска приложения: инициализация базы данных PostgreSQL и
    подключений к Redis и Elasticsearch.
    """
    # Проверяем доступные таблицы в базе данных после инициализации
    logger.info("Проверяем доступные таблицы в базе данных PostgreSQL...")

    async with async_session() as session:
        result = await session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE "
            "table_schema='public';"
        ))
        tables = result.fetchall()
        tables_name = [table[0] for table in tables]

        if not tables_name:
            logger.info("База данных PostgreSQL пуста!")

        else:
            logger.info(
                "В базе данных PostgreSQL найдены таблицы: %s",
                tables_name
            )

    # Инициализация подключения к Redis
    logger.info("Инициализация подключений к Redis...")
    try:
        redis_auth = await get_redis_auth()

        # Проверяем доступность Redis-токен
        if not await redis_auth.redis_client.ping():
            raise ConnectionError("Redis-токен не отвечает на запросы.")

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
    Событие завершения работы приложения: закрытие подключений к Redis и
    Elasticsearch.
    """
    # Закрытие подключений к Redis
    redis_auth = await get_redis_auth()
    if redis_auth:
        await redis_auth.close()


# Подключение роутеров
api_router.include_router(
    user.router, prefix="/auth/users", tags=["Users"]
)
api_router.include_router(
    user_role.router, prefix="/auth/users_role", tags=["Users_role"]
)
api_router.include_router(
    healthcheck.router, prefix="/auth", tags=["healthcheck"]
)

app.include_router(api_router)

# Middleware:
app.add_middleware(AsyncRateLimitMiddleware)
