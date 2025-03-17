import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

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
    try:
        logger.info("Инициализация базы данных PostgreSQL...")

        await create_database()

        # Проверяем доступные таблицы в базе данных после инициализации
        async with async_session() as session:
            result = await session.execute(
                "SELECT table_name FROM information_schema.tables WHERE "
                "table_schema='public';"
            )
            tables = result.fetchall()
            tables_name = [table[0] for table in tables]

            if not tables_name:
                print("База данных PostgreSQL пуста!")

            else:
                print(
                    f"В базе данных PostgreSQL найдены таблицы: {tables_name}"
                )

    except settings.PG_EXCEPTIONS as e:
        logger.error("Ошибка при инициализации базы данных PostgreSQL: %s", e)

        raise ConnectionError(
            "Не удалось инициализировать базу данных PostgreSQL. "
            "Приложение завершает работу."
        )

    # Инициализация подключении к Redis
    try:
        logger.info("Инициализация подключений к Redis...")

        redis_auth = await get_redis_auth()

        # Проверяем доступность Redis-токен
        if not await redis_auth.redis_client.ping():
            raise ConnectionError("Redis-токен не отвечает на запросы.")

        redis_cache = await get_redis_cache()

        # Проверяем доступность Redis-кеш
        if not await redis_cache.redis_client.ping():
            raise ConnectionError("Redis-кеш не отвечает на запросы.")

        logger.info("Подключения к Redis успешно установлено.")

    except settings.REDIS_EXCEPTIONS as e:
        logger.error("Ошибка подключения к Redis: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Redis. Приложение завершает работу."
        )

    # Инициализация подключения к Elasticsearch
    try:
        logger.info("Инициализация подключения к Elasticsearch...")

        es = await get_elastic()

        # Проверяем доступность Elasticsearch
        if not await es.es_client.ping():
            raise ConnectionError("Elasticsearch не отвечает на запросы.")

        logger.info("Подключение к Elasticsearch успешно установлено.")

    except settings.ELASTIC_EXCEPTIONS as e:
        logger.error("Ошибка подключения к Elasticsearch: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Elasticsearch. Приложение завершает "
            "работу."
        )

    logger.info("Все подключения успешно установлены.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие завершения работы приложения: закрытие подключений к Redis и
    Elasticsearch.
    """
    # Закрытие подключений к Redis
    try:
        if redis_auth:
            logger.info("Закрытие подключения к Redis-токен...")

            await redis_auth.close()

            logger.info("Подключение к Redis-токен успешно закрыто.")

        if redis_cache:
            logger.info("Закрытие подключения к Redis-кеш...")

            await redis_cache.close()

            logger.info("Подключение к Redis-кеш успешно закрыто.")

    except settings.REDIS_EXCEPTIONS as e:
        logger.error("Ошибка при закрытии подключений к Redis: %s", e)

    # Закрытие подключения к Elasticsearch
    try:
        if es:
            logger.info("Закрытие подключения к Elasticsearch...")

            await es.close()

            logger.info("Подключение к Elasticsearch успешно закрыто.")

    except settings.ELASTIC_EXCEPTIONS as e:
        logger.error("Ошибка при закрытии подключения к Elasticsearch: %s", e)


# Подключение роутеров
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(healthcheck.router, prefix="/api/v1", tags=["healthcheck"])
