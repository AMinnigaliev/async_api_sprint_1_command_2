from typing import Any

from pydantic import BaseModel, Field


class TaskMetaModel(BaseModel):
    """Meta-информация по задаче."""

    task_id: str | None = Field(default=None, description="ID задачи")
    x_request_id: str | None = Field(default=None, description="ID запроса")
    send_at: str | None = Field(default=None, description="Дата и время отправки задачи на выполнение (iso)")
    execution_at: str | None = Field(default=None, description="Дата и время выполнения задачи (iso)")
    relevance_at: str | None = Field(
        default=None,
        description="До какого периода задача актуальна для выполнения (iso)",
    )


class DefaultTaskModel(BaseModel):
    """Модель данных для Default-задачи."""

    meta: TaskMetaModel
    delivery_methods: list[str] = Field(description="Методы оповещения")
    notification_data: dict[Any, Any] = Field(description="Данные для формирования оповещения")
    task_name: str | None = Field(default=None, description="Наименование задачи")

    @property
    def template_data(self) -> dict[str, Any]:
        return self.notification_data.get("data")

    @property
    def user_ids(self) -> list[str]:
        return self.notification_data.get("user_ids")
