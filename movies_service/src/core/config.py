import os
from asyncpg.exceptions import \
    ConnectionDoesNotExistError as PGConnectionDoesNotExistError
from asyncpg.exceptions import PostgresError
from asyncpg.exceptions import SyntaxOrAccessError as PGSyntaxOrAccessError
from elastic_transport import TransportError as ESTransportError
from elasticsearch import ApiError as ESApiError
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from redis.exceptions import RedisError
from typing import Any


class Settings(BaseSettings):
    project_name: str = Field("movies", env="PROJECT_NAME")
    service_name: str = Field("movies_service", env="MOVIES_SERVICE_NAME")
    env_type: str = Field("prod", env="ENV_TYPE")
    base_dir: str = Field(
        default_factory=lambda: os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    @computed_field
    @property
    def is_prod_env(self) -> bool:
        """
        Флаг, указывает какое используется окружение.
        - prod:
        - develop: устанавливается при разработке.

        @rtype: bool
        @return:
        """
        return self.env_type == "prod"

    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: str = Field("password", env="REDIS_PASSWORD")
    redis_rate_limit_db: int = Field(1, env="REDIS_RATE_LIMIT_DB")

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

    jaeger_host: str = Field("jaeger", env="JAEGER_HOST")
    jaeger_port: int = Field(4318, env="JAEGER_PORT")

    @computed_field
    @property
    def jaeger_http_endpoint(self) -> str:
        return f"http://{self.jaeger_host}:{self.jaeger_port}/v1/traces"

    elastic_exceptions: Any = (ESApiError, ESTransportError)
    redis_exceptions: Any = (RedisError,)
    pg_exceptions: Any = (
        PostgresError, PGConnectionDoesNotExistError, PGSyntaxOrAccessError
    )

    elastic_response_size: int = 1000
    cache_expire_in_seconds: int = 300

    rate_limit: int = Field(5, env="RATE_LIMIT")
    rate_limit_window: int = Field(60, env="RATE_LIMIT_WINDOW")

    @computed_field
    @property
    def redis_rate_limit_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_rate_limit_db}"


settings = Settings()
