import os
from functools import cached_property
from pydantic_settings import BaseSettings, SettingsConfigDict, Field


class Settings(BaseSettings):
    """Конфигурация WebSocket-Sender через переменные окружения и .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "websocket_sender"

    # ----- RabbitMQ ---------------------------------------------------------
    rabbit_host: str = "rabbitmq"
    rabbit_port: int = 5672
    rabbit_user: str = "guest"
    rabbit_password: str = "guest"
    rabbit_vhost: str = "/"

    # очередь, в которую notification-worker публикует WebSocket-уведомления
    websocket_queue: str = Field(default="websocket", alias="WEBSOCKET_QUEUE_NAME")

    # ----- Auth / Observability --------------------------------------------
    secret_key: str = "practix"
    algorithm: str = "HS256"
    sentry_dsn: str | None = None
    jaeger_host: str = "jaeger"
    jaeger_port: int = 6831
    prometheus_metrics: bool = True

    # -----------------------------------------------------------------------

    @cached_property
    def amqp_url(self) -> str:
        return (
            f"amqp://{self.rabbit_user}:{self.rabbit_password}"
            f"@{self.rabbit_host}:{self.rabbit_port}{self.rabbit_vhost}"
        )


settings = Settings()
