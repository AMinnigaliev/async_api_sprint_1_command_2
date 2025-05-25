from datetime import datetime
from uuid import UUID

from bson import ObjectId
from pydantic import BaseModel, Field


class FilmRatingCreateUpdate(BaseModel):
    rating: int = Field(
        ..., ge=1, le=10, description="Пользовательская оценка фильма"
    )


class BaseResponse(BaseModel):
    film_id: UUID = Field(..., description="ID фильма")
    created_at: datetime = Field(
        ..., description="Дата и время создания записи"
    )
    modified_at: datetime | None = Field(
        None, description="Дата и время изменения записи"
    )


class FilmRatingResponse(BaseResponse, FilmRatingCreateUpdate):
    _id: ObjectId = Field(
        ..., description="ID оценки", serialization_alias="rating_id")
    user_id: UUID = Field(..., description="ID пользователя")


class AmtAvgFilmRatingResponse(BaseResponse):
    _id: ObjectId = Field(
        ...,
        description="Уникальный идентификатор записи",
        serialization_alias="amt_avg_id",
    )
    amount_ratings: int = Field(
        ..., description="Количество пользовательских оценок фильма"
    )
    average_rating: int = Field(
        ..., ge=1, le=10, description="Средняя пользовательская оценка фильма"
    )


class DeleteFilmRatingResponse(BaseModel):
    message: str = Field(
        ...,
        description="Сообщение об удачном удалении пользовательской оценки "
                    "фильма",
    )
