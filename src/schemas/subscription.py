from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionCreateUpdate(BaseModel):
    """Модель для создания новой или редактирования подписки."""
    name: str = Field(
        ..., min_length=1, max_length=255, description="Название подписки"
    )
    description: str | None = Field(None, description="Описание подписки")


class SubscriptionResponse(SubscriptionCreateUpdate):
    """Модель для представления информации о подписке."""
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")

    model_config = {"from_attributes": True}
