from typing import Any, AsyncGenerator

import pytest
import redis
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from sqlalchemy import create_engine, engine, orm

from settings import config


@pytest_asyncio.fixture
async def es_client() -> AsyncGenerator[AsyncElasticsearch, Any]:
    """
    Создает экземпляр клиента Elasticsearch для тестов.

    @rtype AsyncGenerator[AsyncElasticsearch, Any]:
    @return client:
    """
    client = AsyncElasticsearch(
        hosts="http://{}:{}/".format(config.elastic_host, config.elastic_port),
        basic_auth=(config.elastic_name, config.elastic_password),
        request_timeout=config.request_timeout,
    )

    try:
        yield client

    finally:
        await client.close()


@pytest.fixture(scope="session")
def redis_client():
    redis_client = redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_password,
        db=config.redis_db,
    )

    try:
        yield redis_client

    finally:
        redis_client.close()


@pytest.fixture(scope="session")
def clear_redis(redis_client):
    redis_client.flushall()
    yield


@pytest.fixture(scope="session")
def pg_session():
    pg_url = engine.URL.create(
        drivername=config.postgres_driver_name,
        database=config.postgres_db,
        username=config.postgres_user,
        password=config.postgres_password,
        host=config.postgres_host,
        port=config.postgres_port,
    )

    new_engine = create_engine(pg_url, echo=True)
    session_local = orm.sessionmaker(bind=new_engine)

    with session_local() as session:
        yield session
