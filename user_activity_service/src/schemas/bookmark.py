from datetime import datetime
from uuid import UUID

from bson import ObjectId
from pydantic import BaseModel, Field


class BookmarkResponse(BaseModel):
    _id: ObjectId = Field(
        ..., description="ID закладки", serialization_alias="bookmark_id"
    )
    user_id: UUID = Field(..., description="ID пользователя")
    film_id: UUID = Field(..., description="ID фильма")
    created_at: datetime = Field(
        ..., description="Дата и время создания закладки"
    )


class DeleteBookmarkResponse(BaseModel):
    message: str = Field(
        ..., description="Сообщение об удачном удалении закладки на фильм"
    )
