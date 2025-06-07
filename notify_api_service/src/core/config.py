import os
from typing import Any

from aio_pika.exceptions import (AMQPConnectionError, ChannelClosed,
                                 DeliveryError)
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


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

    rabbit_scheme: str = Field("amqp", alias="RABBIT_SCHEME")
    rabbit_host: str = Field("rabbit", alias="RABBIT_HOST")
    rabbit_login: str = Field("login", alias="RABBIT_LOGIN")
    rabbit_password: str = Field("password", alias="RABBIT_PASSWORD")

    jaeger_host: str = Field("jaeger", alias="JAEGER_HOST")
    jaeger_port: int = Field(4318, alias="JAEGER_PORT")
    enable_jaeger: bool = Field(True, alias="ENABLE_JAEGER")

    rabbit_exceptions: Any = (
        AMQPConnectionError,
        ChannelClosed,
        DeliveryError,
    )

    @computed_field
    @property
    def jaeger_http_endpoint(self) -> str:
        return f"http://{self.jaeger_host}:{self.jaeger_port}/v1/traces"

    @computed_field
    @property
    def rabbit_url(self) -> str:
        return (
            f"{self.rabbit_scheme}://{self.rabbit_login}:"
            f"{self.rabbit_password}@{self.rabbit_host}/"
        )


settings = Settings()
