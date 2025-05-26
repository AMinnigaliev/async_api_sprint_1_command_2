import os
from functools import cached_property
from typing import Any

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from pymongo.errors import ConnectionFailure as MongoConnectionFailure
from pymongo.errors import OperationFailure as MongoOperationFailure
from redis.exceptions import RedisError


class Settings(BaseSettings):
    project_name: str = Field("movies", alias="PROJECT_NAME")
    service_name: str = Field("movies_service", alias="MOVIES_SERVICE_NAME")
    env_type: str = Field("prod", alias="ENV_TYPE")
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

    auth_service_host: str = Field(
        default="localhost", alias="AUTH_SERVICE_HOST"
    )
    auth_service_port: int = Field(default=8000, alias="AUTH_SERVICE_PORT")

    movies_service_host: str = Field(
        default="localhost", alias="MOVIES_SERVICE_HOST"
    )
    movies_service_port: int = Field(default=8000, alias="MOVIES_SERVICE_PORT")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")
    redis_rate_limit_db: int = Field(default=1, alias="REDIS_RATE_LIMIT_DB")

    mongo_name: str = Field(default="name", alias="MONGO_NAME")
    mongo_server_selection_timeout_ms: int = 5000
    mongo_max_pool_size: int = 100

    jaeger_host: str = Field("jaeger", alias="JAEGER_HOST")
    jaeger_port: int = Field(4318, alias="JAEGER_PORT")
    enable_jaeger: bool = Field(True, alias="ENABLE_JAEGER")

    @computed_field
    @property
    def jaeger_http_endpoint(self) -> str:
        return f"http://{self.jaeger_host}:{self.jaeger_port}/v1/traces"

    redis_exceptions: Any = (RedisError,)
    mongo_exceptions: Any = (MongoConnectionFailure, MongoOperationFailure)

    # Безопасность
    login_url: str = "/api/v1/auth/users/login"
    secret_key: str = Field(default="practix", alias="SECRET_KEY")
    algorithm: str = "HS256"

    cache_expire_in_seconds: int = 300

    rate_limit: int = Field(5, alias="RATE_LIMIT")
    rate_limit_window: int = Field(60, alias="RATE_LIMIT_WINDOW")

    @computed_field
    @property
    def redis_rate_limit_url(self) -> str:
        return (
            f"redis://:{self.redis_password}@{self.redis_host}:"
            f"{self.redis_port}/{self.redis_rate_limit_db}"
        )

    @computed_field
    @property
    def mongo_uri(self) -> str:
        """
        Подключение к двум mongos с fail-over и без привязки к одному хосту.
        """
        hosts = "mongos1:27018,mongos2:27017"
        return (
            f"mongodb://{hosts}/{self.mongo_name}?directConnection=false"
        )

    @cached_property
    def auth_service_url(self) -> str:
        return (
            f"http://{self.auth_service_host}:{self.auth_service_port}"
            f"/api/v1/auth"
        )

    @cached_property
    def movies_service_url(self) -> str:
        return (
            f"http://{self.movies_service_host}:{self.movies_service_port}"
            f"/api/v1/movies/films"
        )


settings = Settings()
