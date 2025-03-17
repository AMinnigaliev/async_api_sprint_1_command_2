from uuid import UUID
from pydantic import BaseModel


class BaseUser(BaseModel):
    first_name: str
    last_name: str


class UserCreate(BaseUser):
    login: str
    password: str


class UserInDB(BaseUser):
    id: UUID

    class Config:
        orm_mode = True
