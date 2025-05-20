from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FilmRatingCreateUpdate(BaseModel):
    rating: int = Field(
        ..., ge=1, le=10, description="Пользовательская оценка фильма"
    )


class BaseResponse(BaseModel):
    film_id: UUID = Field(..., description="ID фильма")
    created: datetime = Field(
        ..., description="Дата и время создания записи"
    )
    modified: datetime | None = Field(
        None, description="Дата и время изменения записи"
    )


class FilmRatingResponse(BaseResponse, FilmRatingCreateUpdate):
    rating_id: UUID = Field(..., description="ID оценки")
    user_id: UUID = Field(..., description="ID пользователя")


class AmountFilmRatingResponse(BaseResponse):
    amount_ratings: int = Field(
        ..., description="Количество пользовательских оценок фильма"
    )


class AverageFilmRatingResponse(BaseResponse):
    average_rating: int = Field(
        ..., ge=1, le=10, description="Средняя пользовательская оценка фильма"
    )


class DeleteFilmRatingResponse(BaseModel):
    message: str = Field(
        ...,
        description="Сообщение об удачном удалении пользовательской оценки "
                    "фильма",
    )
