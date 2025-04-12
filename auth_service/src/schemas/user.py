from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    login: str
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    oauth_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    created_at: datetime

    class Config:
        orm_mode = True
