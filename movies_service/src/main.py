import logging

from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse
from sqlalchemy import text

from src.api.v1 import films, genres, healthcheck, persons
from src.core.config import settings
from src.db.elastic import get_elastic
from src.db.postgres import async_session
from src.db.redis_client import get_redis_cache

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/movies/openapi',
    openapi_url='/api/movies/openapi.json',
    default_response_class=ORJSONResponse,
)
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
    logger.info("Инициализация подключения к Redis...")
    try:
        redis_cache = await get_redis_cache()

        # Проверяем доступность Redis-кеш
        if not await redis_cache.redis_client.ping():
            raise ConnectionError("Redis-кеш не отвечает на запросы.")

    except settings.REDIS_EXCEPTIONS as e:
        logger.error("Ошибка подключения к Redis: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Redis. Приложение завершает работу."
        )

    else:
        logger.info("Подключение к Redis успешно установлено.")

    # Инициализация подключения к Elasticsearch
    logger.info("Инициализация подключения к Elasticsearch...")
    try:
        es = await get_elastic()

        # Проверяем доступность Elasticsearch
        if not await es.es_client.ping():
            raise ConnectionError("Elasticsearch не отвечает на запросы.")

    except settings.ELASTIC_EXCEPTIONS as e:
        logger.error("Ошибка подключения к Elasticsearch: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Elasticsearch. Приложение завершает "
            "работу."
        )

    else:
        logger.info("Подключение к Elasticsearch успешно установлено.")

    logger.info("Все подключения успешно установлены.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие завершения работы приложения: закрытие подключений к Redis и
    Elasticsearch.
    """
    # Закрытие подключения к Redis
    redis_cache = await get_redis_cache()
    if redis_cache:
        await redis_cache.close()

    # Закрытие подключения к Elasticsearch
    es = await get_elastic()
    if es:
        await es.close()


# Подключение роутеров
api_router.include_router(
    films.router, prefix="/movies/films", tags=["films"]
)
api_router.include_router(
    persons.router, prefix="/movies/persons", tags=["persons"]
)
api_router.include_router(
    genres.router, prefix="/movies/genres", tags=["genres"]
)
api_router.include_router(
    healthcheck.router, prefix="/movies", tags=["healthcheck"]
)

app.include_router(api_router)
