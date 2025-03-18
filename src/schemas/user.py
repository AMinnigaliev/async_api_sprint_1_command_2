from uuid import UUID
from datetime import datetime
from typing import Union
from pydantic import BaseModel


class BaseUser(BaseModel):
    """Базовая модель пользователя."""
    first_name: str
    last_name: str


class UserCreate(BaseUser):
    """Модель для создания пользователя."""
    login: str
    password: str


class UserInDB(BaseUser):
    """Модель пользователя в базе данных."""
    id: UUID

    class Config:
        from_attributes = True


class LoginHistory(BaseModel):
    """Модель истории входов пользователя."""
    login_time: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Модель токена для аутентификации."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    """Модель для обновления данных пользователя."""
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    password: Union[str, None] = None
