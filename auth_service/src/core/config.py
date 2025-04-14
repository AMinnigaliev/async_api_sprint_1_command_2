import os
from typing import Any, ClassVar

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from redis.exceptions import RedisError
from asyncpg.exceptions import PostgresError
from asyncpg.exceptions import SyntaxOrAccessError as PGSyntaxOrAccessError
from asyncpg.exceptions import ConnectionDoesNotExistError as PGConnectionDoesNotExistError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.exc import OperationalError as SQLOperationalError


class Settings(BaseSettings):
    project_name: str = Field(default="movies", env="PROJECT_NAME")
    service_name: str = Field("auth_service", env="AUTH_SERVICE_NAME")
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

    elastic_host: str = Field("elasticsearch", env="ELASTIC_HOST")
    elastic_port: int = Field(9200, env="ELASTIC_PORT")
    elastic_scheme: str = Field("http", env="ELASTIC_SCHEME")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_password: str = Field(default="123qwe", alias="ES_PASSWORD")

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

    # Exceptions
    redis_exceptions: Any = (RedisError,)
    pg_exceptions: Any = (
        PostgresError, PGConnectionDoesNotExistError, PGSyntaxOrAccessError
    )
    sql_exceptions: Any = (
        SQLAlchemyError, SQLIntegrityError, SQLOperationalError
    )

    # Безопасность
    token_revoke: ClassVar[bytes] = b"revoked"
    token_active: ClassVar[bytes] = b"active"
    secret_key: str = Field("practix", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


settings = Settings()
