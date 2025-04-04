import os
from asyncpg.exceptions import \
    ConnectionDoesNotExistError as PGConnectionDoesNotExistError
from asyncpg.exceptions import PostgresError
from asyncpg.exceptions import SyntaxOrAccessError as PGSyntaxOrAccessError
from elastic_transport import TransportError as ESTransportError
from elasticsearch import ApiError as ESApiError
from pydantic import Field
from pydantic_settings import BaseSettings
from redis.exceptions import RedisError
from typing import Any


class Settings(BaseSettings):
    # Общая конфигурация
    PROJECT_NAME: str = Field("movies", env="PROJECT_NAME")

    # Конфигурация Redis
    REDIS_HOST: str = Field("redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field("password", env="REDIS_PASSWORD")

    # Конфигурация Elasticsearch
    ELASTIC_HOST: str = Field("elasticsearch", env="ELASTIC_HOST")
    ELASTIC_PORT: int = Field(9200, env="ELASTIC_PORT")
    ELASTIC_SCHEME: str = Field("http", env="ELASTIC_SCHEME")
    ELASTIC_NAME: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    ELASTIC_PASSWORD: str = Field(default="123qwe", alias="ELASTIC_PASSWORD")

    # Конфигурация PostgreSQL
    PG_USER: str = Field("user", env="PG_USER")
    PG_PASSWORD: str = Field("password", env="PG_PASSWORD")
    PG_HOST: str = Field("postgres", env="PG_HOST")
    PG_PORT: int = Field(5432, env="PG_PORT")
    PG_NAME: str = Field("name", env="PG_NAME")

    # Директория проекта
    BASE_DIR: str = Field(
        default_factory=lambda: os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    # Исключения
    ELASTIC_EXCEPTIONS: Any = (ESApiError, ESTransportError)
    REDIS_EXCEPTIONS: Any = (RedisError,)
    PG_EXCEPTIONS: Any = (
        PostgresError, PGConnectionDoesNotExistError, PGSyntaxOrAccessError
    )

    # Прочее
    ELASTIC_RESPONSE_SIZE: int = 1000
    CACHE_EXPIRE_IN_SECONDS: int = 300


# Инициализация настроек
settings = Settings()
