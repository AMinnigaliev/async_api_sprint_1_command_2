from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PayloadResponse(BaseModel):
    """Модель для представления payload токена."""
    user_id: UUID = Field(
        ..., description="Уникальный идентификатор пользователя"
    )
    role: str = Field(..., description="Роль пользователя")
    exp: datetime = Field(..., description="Срок действия токена")

    model_config = {"from_attributes": True}
