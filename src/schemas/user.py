from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionCreateUpdate(BaseModel):
    """Модель для создания новой подписки."""
    name: str = Field(
        ..., min_length=1, max_length=255, description="Название подписки"
    )
    description: str | None = Field(None, description="Описание подписки")


class SubscriptionResponse(SubscriptionCreateUpdate):
    """Модель для представления информации о подписке."""
    id: int = Field(..., description="Уникальный идентификатор подписки")

    model_config = {"from_attributes": True}


class BaseUser(BaseModel):
    """Базовая модель пользователя с основными данными."""
    first_name: str | None = Field(
        None, min_length=1, max_length=100, description="Имя пользователя"
    )
    last_name: str | None = Field(
        None, min_length=1, max_length=100, description="Фамилия пользователя"
    )


class UserCreate(BaseUser):
    """Модель для создания нового пользователя."""
    login: str = Field(
        ..., min_length=1, max_length=100, description="Логин пользователя"
    )
    password: str = Field(
        ..., min_length=8, max_length=150, description="Пароль пользователя"
    )


class UserResponse(BaseUser):
    """Модель для представления информации о пользователе."""
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    role: str = Field(..., discriminator="Роль пользователя")
    subscriptions: list[SubscriptionResponse] = Field(
        default_factory=[], description="Подписки пользователя"
    )

    model_config = {"from_attributes": True}
