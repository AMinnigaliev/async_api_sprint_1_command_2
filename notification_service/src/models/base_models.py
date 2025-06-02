from typing import Any

from pydantic import BaseModel, Field


class TaskMetaModel(BaseModel):
    """Meta-информация по задаче."""

    task_id: str = Field(description="ID задачи")
    x_request_id: str | None = Field(default=None, description="ID запроса")
    send_at: str | None = Field(default=None, description="Дата и время отправки задачи на выполнение")
    execution_at: str | None = Field(default=None, description="Дата и время выполнения задачи")
    relevance_at: str | None = Field(default=None, description="До какого периода задача актуальна для выполнения")


class DefaultTaskModel(BaseModel):
    """Модель данных для Default-задачи."""

    meta: TaskMetaModel
    delivery_methods: list[str] = Field(description="Метод оповещения")
    task_name: str = Field(description="Наименование задачи")
    notification_data: dict[Any, Any] = Field(description="Данные для формирования оповещения")
