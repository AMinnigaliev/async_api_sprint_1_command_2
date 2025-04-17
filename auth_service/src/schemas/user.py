from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    login: str = Field(..., description="Логин пользователя")
    password: str | None = Field(None, description="Пароль пользователя")
    email: EmailStr | None = Field(None, description="Email пользователя")
    oauth_id: str | None = Field(None, description="OAuth‑ID (например, от Яндекса)")
    first_name: str | None = Field(None, description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: str | None = Field(None, description="Новый email пользователя")
    username: str | None = Field(None, description="Новый логин пользователя")
    password: str | None = Field(None, description="Новый пароль пользователя")

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., description="Логин пользователя")
    created_at: datetime = Field(..., description="Дата и время создания аккаунта")

    class Config:
        orm_mode = True
