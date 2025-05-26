from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BookmarkResponse(BaseModel):
    bookmark_id: str = Field(..., description="ID закладки")
    user_id: UUID = Field(..., description="ID пользователя")
    film_id: UUID = Field(..., description="ID фильма")
    created_at: datetime = Field(
        ..., description="Дата и время создания закладки"
    )


class DeleteBookmarkResponse(BaseModel):
    message: str = Field(
        ..., description="Сообщение об удачном удалении закладки на фильм"
    )
