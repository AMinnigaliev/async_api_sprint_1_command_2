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
    project_name: str = Field("movies", env="PROJECT_NAME")
    BASE_DIR: str = Field(
        default_factory=lambda: os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: str = Field("password", env="REDIS_PASSWORD")

    elastic_host: str = Field("elasticsearch", env="ELASTIC_HOST")
    elastic_port: int = Field(9200, env="ELASTIC_PORT")
    elastic_scheme: str = Field("http", env="ELASTIC_SCHEME")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_password: str = Field(default="123qwe", alias="ELASTIC_PASSWORD")

    pg_user: str = Field("user", env="PG_USER")
    pg_password: str = Field("password", env="PG_PASSWORD")
    pg_host: str = Field("postgres", env="PG_HOST")
    pg_port: int = Field(5432, env="PG_PORT")
    pg_name: str = Field("name", env="PG_NAME")

    elastic_exceptions: Any = (ESApiError, ESTransportError)
    redis_exceptions: Any = (RedisError,)
    pg_exceptions: Any = (
        PostgresError, PGConnectionDoesNotExistError, PGSyntaxOrAccessError
    )

    elastic_response_size: int = 1000
    cache_expire_in_seconds: int = 300


settings = Settings()
