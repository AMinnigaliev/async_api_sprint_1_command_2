from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    rating_id: str = Field(..., description="ID оценки")
    user_id: UUID = Field(..., description="ID пользователя")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )


class AmtAvgFilmRatingResponse(BaseResponse):
    amt_avg_id: str = Field(
        ..., description="Уникальный идентификатор записи"
    )
    amount_ratings: int = Field(
        ..., description="Количество пользовательских оценок фильма"
    )
    average_rating: int = Field(
        ..., ge=1, le=10, description="Средняя пользовательская оценка фильма"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )


class DeleteFilmRatingResponse(BaseModel):
    message: str = Field(
        ...,
        description="Сообщение об удачном удалении пользовательской оценки "
                    "фильма",
    )
