from pydantic import BaseModel, Field
from uuid import UUID


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


class UserUpdate(BaseUser):
    """Модель для обновления данных пользователя."""
    password: str | None = Field(
        None, min_length=8, max_length=150, description="Пароль пользователя"
    )


class UserResponse(BaseUser):
    """Модель для представления информации о пользователе."""
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    login: str = Field(
        ..., min_length=1, max_length=100, description="Логин пользователя"
    )
    role: str = Field(..., description="Роль пользователя")

    model_config = {"from_attributes": True}
