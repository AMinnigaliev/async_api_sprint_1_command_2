from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BookmarkResponse(BookmarkCreate):
    bookmark_id: UUID = Field(..., description="ID закладки")
    user_id: UUID = Field(..., description="ID пользователя")
    film_id: UUID = Field(..., description="ID фильма")
    created: datetime = Field(
        ..., description="Дата и время создания закладки"
    )


class DeleteBookmarkResponse(BaseModel):
    message: str = Field(
        ..., description="Сообщение об удачном удалении закладки на фильм"
    )
