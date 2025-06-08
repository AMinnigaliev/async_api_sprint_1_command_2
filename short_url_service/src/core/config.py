import os
from typing import Any

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
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

    domain: str = Field("short.local", alias="DOMAIN")

    redis_host: str = Field("redis", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_password: str = Field("password", alias="REDIS_PASSWORD")
    redis_short_url_db: int = 14

    jaeger_host: str = Field("jaeger", alias="JAEGER_HOST")
    jaeger_port: int = Field(4318, alias="JAEGER_PORT")
    enable_jaeger: bool = Field(True, alias="ENABLE_JAEGER")

    redis_exceptions: Any = (RedisError,)

    short_url_expire: int = 7776000
    code_length: int = 10

    @computed_field
    @property
    def jaeger_http_endpoint(self) -> str:
        return f"http://{self.jaeger_host}:{self.jaeger_port}/v1/traces"


settings = Settings()
