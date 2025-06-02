import os
from typing import Any

from kombu import Exchange, Queue
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):
    """Base configs."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = Field(default="movies", alias="PROJECT_NAME")
    service_name: str = Field(default="notification_service", alias="NOTIFICATION_SERVICE_NAME")
    env_type: str = Field(default="prod", alias="ENV_TYPE")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_format: str = Field(default="%(asctime)s - %(levelname)s - %(message)s", alias="LOG_FORMAT")

    # RabbitMQ:
    rmq_user: str = Field(default="guest", alias="RABBITMQ_DEFAULT_USER")
    rmq_password: str  = Field(default="guest", alias="RABBITMQ_DEFAULT_PASS")
    rmq_host: str  = Field(default="localhost", alias="RABBITMQ_HOST")
    rmq_port: str | int  = Field(default=5672, alias="RABBITMQ_PORT")
    rmq_vhost: str  = Field(default="/", alias="RABBITMQ_VHOST")

    # Postgres
    postgres_driver: str = Field(default="postgresql", alias="PG_DRIVER_NAME")
    postgres_db: str = Field(default="postgres", alias="PG_NAME")
    postgres_user: str = Field(default="user", alias="PG_USER")
    postgres_password: str = Field(default="password", alias="PG_PASSWORD")
    postgres_host: str = Field(default="127.0.0.1", alias="PG_HOST")
    postgres_port: int = Field(default=5432, alias="PG_PORT")


class CeleryConfigs(Configs):
    """Base + Celery configs."""

    # Base
    @computed_field
    @property
    def broker_url(self) -> str:
        return os.getenv(
            "CELERY_BROKER_URL",
            default=f"amqp://{self.rmq_user}:{self.rmq_password}@{self.rmq_host}:{self.rmq_port}{self.rmq_vhost}",
        )
    @computed_field
    @property
    def backend_url(self) -> str:
        return os.getenv(
            "CELERY_BACKEND_URL",
            default=(
                f"db+{self.postgres_driver}://{self.postgres_user}:{self.postgres_password}@"
                f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            ),
        )

    # Serialization task
    task_serializer: str = Field(
        default="json",
        alias="CELERY_TASK_SERIALIZER",
        description="Сериализатор задач",
    )
    result_serializer: str = Field(
        default="json",
        alias="CELERY_RESULT_SERIALIZER",
        description="Сериализатор результата задач",
    )
    accept_content: list[str] = Field(
        default=["json", ],
        alias="CELERY_ACCEPT_CONTENT",
        description="Разрешенный тип данных для задач",
    )

    # Timezone
    enable_utc: bool = Field(default=True, alias="CELERY_ENABLE_UTC")
    timezone: str = Field(default="Europe/Moscow", alias="CELERY_TIMEZONE")

    # Worker
    worker_prefetch_multiplier: int = Field(
        default=1,
        alias="CELERY_WORKER_PREFETCH_MULTIPLIER",
        description="Количество задач, которые worker берет за раз",
    )
    worker_max_tasks_per_child: int = Field(
        default=100,
        alias="CELERY_WORKER_MAX_TASKS_PER_CHILD",
        description="Перезапуск worker после N кол-ва выполненных задач (позволяет устранить утечку памяти)",
    )
    worker_max_memory_per_child: int = Field(
        default=250_000,  # ~ 250MB
        alias="CELERY_WORKER_PREFETCH_MULTIPLIER",
        description="Контроль потребления памятью для 1 задачи (максимум потребления памяти 1 задачей)",
    )

    # Tasks:
    task_acks_late: bool = True  # подтверждение после выполнения задачи
    task_reject_on_worker_lost: bool = True  # повторная постановка при потере worker
    task_track_started: bool = True  # отслеживание начала выполнения
    task_annotations: dict = {
        "*": {
            "retry": True,
            "retry_policy": {
                "max_retries": 1,
                "interval_start": 0,
                "interval_step": 0.5,
                "interval_max": 1.0,
            }
        }
    }

    # Groups
    default_group: str = "default"
    real_time_group: str = "real_time"
    deferred_group: str = "deferred"

    # Exchanges by groups
    @computed_field
    @property
    def exchanges(self) -> dict[str, Exchange]:
        return {
            self.default_group: Exchange(name=self.default_group, type="direct", durable=True),
            self.real_time_group: Exchange(name=self.real_time_group, type="direct", durable=True),
            self.deferred_group: Exchange(name=self.deferred_group, type="direct", durable=True),
        }

    # Queues by groups
    @computed_field
    @property
    def task_queues(self) -> tuple[Queue, ...]:
        return (
            Queue(
                name=self.default_group,
                exchange=self.exchanges[self.default_group],
            ),
            Queue(
                name=self.real_time_group,
                exchange=self.exchanges[self.real_time_group],
            ),
            Queue(
                name=self.deferred_group,
                exchange=self.exchanges[self.deferred_group],
            ),
        )

    # Tasks by groups
    @computed_field
    @property
    def task_routes(self) -> dict[str, dict[str, Any]]:
        return {
            "tasks.default.default_task": {"queue": self.default_group},
            f"tasks.{self.real_time_group}.*": {"queue": self.real_time_group},
            f"tasks.{self.deferred_group}.*": {"queue": self.deferred_group},
        }


config = Configs()
celery_config = CeleryConfigs()
