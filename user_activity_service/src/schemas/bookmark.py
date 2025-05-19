from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BookmarkCreateDelete(BaseModel):
    film_id: UUID = Field(..., description="ID фильма")


class BookmarkResponse(BookmarkCreateDelete):
    bookmark_id: UUID = Field(..., description="ID закладки")
    user_id: UUID = Field(..., description="ID пользователя")
    created: datetime = Field(
        ..., description="Дата и время создания закладки"
    )


class DeleteBookmarkResponse(BaseModel):
    message: str = Field(
        ..., description="Сообщение об удачном удалении закладки на фильм"
    )
