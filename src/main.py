import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy import text

from src.api.v1 import films, genres, persons, user, healthcheck
from src.core.config import settings
from src.db.elastic import es, get_elastic
from src.db.init_postgres import create_database
from src.db.postgres import async_session
from src.db.redis_client import (redis_auth, get_redis_auth, redis_cache,
                                 get_redis_cache)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    """
    Событие запуска приложения: инициализация базы данных PostgreSQL и
    подключений к Redis и Elasticsearch.
    """
    # Инициализация PostgreSQL
    logger.info("Инициализация базы данных PostgreSQL...")
    try:
        await create_database()

    except settings.PG_EXCEPTIONS as e:
        logger.error("Ошибка при инициализации базы данных PostgreSQL: %s", e)

        raise ConnectionError(
            "Не удалось инициализировать базу данных PostgreSQL. "
            "Приложение завершает работу."
        )

    else:
        # Проверяем доступные таблицы в базе данных после инициализации
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
                    f"В базе данных PostgreSQL найдены таблицы: %s",
                    tables_name
                )

    # Инициализация подключении к Redis
    logger.info("Инициализация подключений к Redis...")
    try:
        redis_auth = await get_redis_auth()

        # Проверяем доступность Redis-токен
        if not await redis_auth.redis_client.ping():
            raise ConnectionError("Redis-токен не отвечает на запросы.")

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
        logger.info("Подключения к Redis успешно установлено.")

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
    # Закрытие подключений к Redis
    if redis_auth:
        await redis_auth.close()

    if redis_cache:
        await redis_cache.close()

    # Закрытие подключения к Elasticsearch
    if es:
        await es.close()


# Подключение роутеров
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(healthcheck.router, prefix="/api/v1", tags=["healthcheck"])
