from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class NotificationPayload(BaseModel):
    title: str | None = Field(
        None, description="Заголовок уведомления (необязательно)"
    )
    body: str = Field(..., description="Текст уведомления")
    url: HttpUrl | None = Field(None, description="Ссылка (необязательно)")


class NotificationData(BaseModel):
    user_ids: list[str] = Field(
        ..., description="Список ID пользователей"
    )
    to_all_users: bool = Field(..., description="Отправить всем пользователям")
    data: NotificationPayload = Field(..., description="Данные для шаблона")


class Meta(BaseModel):
    send_at: datetime = Field(
        ..., description="Время постановки задачи в очередь"
    )
    execution_at: datetime = Field(..., description="Время выполнения задачи")
    relevance_at: datetime = Field(
        ..., description="Актуальность задачи до момента"
    )


class Kwargs(BaseModel):
    meta: Meta = Field(..., description="Метаданные задачи")
    delivery_methods: list[str] = Field(..., description="Методы доставки")
    notification_type: str = Field(..., description="Тип уведомления")
    notification_data: NotificationData = Field(
        ..., description="Основные данные уведомления"
    )


class IncomingMessage(BaseModel):
    id: str = Field(..., description="ID задачи (UUID от админки)")
    kwargs: Kwargs = Field(..., description="Параметры для выполнения задачи")


class EnrichedMeta(Meta):
    X_Request_Id: str = Field(
        ..., alias="X-Request-Id", description="ID запроса (X-Request-ID)"
    )


class EnrichedKwargs(Kwargs):
    meta: EnrichedMeta = Field(..., description="Метаданные задачи")


class EnrichedMessage(IncomingMessage):
    task: str = Field("default", description="Наименование Celery-задачи")
    kwargs: EnrichedKwargs = Field(
        ..., description="Параметры для выполнения задачи"
    )
