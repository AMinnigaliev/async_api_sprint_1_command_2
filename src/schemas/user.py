from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from src.schemas.subscription import SubscriptionResponse


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
    role: str = Field(..., description="Роль пользователя")
    subscriptions: list[SubscriptionResponse] = Field(
        default_factory=[], description="Подписки пользователя"
    )

    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """Модель пользователя для внутреннего использования (например, в БД)."""
    hashed_password: str = Field(..., description="Хэшированный пароль")

    model_config = {"from_attributes": True}

class Token(BaseModel):
    """Модель JWT-токена для ответа на аутентификацию и обновление."""
    access_token: str = Field(..., description="JWT access-токен")
    refresh_token: str = Field(..., description="JWT refresh-токен")
    token_type: str = Field(default="bearer", description="Тип токена")

class LoginHistory(BaseModel):
    """Модель записи истории входов пользователя."""
    id: UUID = Field(..., description="Уникальный идентификатор записи")
    user_id: UUID = Field(..., description="ID пользователя")
    user_agent: str = Field(..., description="User-Agent клиента")
    ip_address: str = Field(..., description="IP-адрес клиента")
    timestamp: datetime = Field(..., description="Дата и время входа")

    model_config = {"from_attributes": True}