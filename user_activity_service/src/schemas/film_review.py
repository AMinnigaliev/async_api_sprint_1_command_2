from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    review_id: UUID = Field(..., description="ID рецензии")
    likes: int = Field(0, ge=0, description="Количество лайков рецензии")
    dislikes: int = Field(0, ge=0, description="Количество дизлайков рецензии")


class ReviewRatingCreateUpdate(BaseModel):
    review_like: bool = Field(..., description="Понравилась рецензия или нет")


class ReviewRatingResponse(BaseResponse):
    pass

class FilmReviewCreateUpdate(BaseModel):
    review: str = Field(..., description="Текст рецензии")


class BaseFilmReviewResponse(BaseResponse, FilmReviewCreateUpdate):
    users_film_rating: int | None = Field(
        None, ge=1, le=10, description="Пользовательская оценка фильма"
    )


class FilmReviewResponse(BaseFilmReviewResponse):
    user_id: UUID = Field(..., description="ID пользователя")
    film_id: UUID = Field(..., description="ID фильма")
    created: datetime = Field(
        ..., description="Дата и время создания записи"
    )
    modified: datetime | None = Field(
        None, description="Дата и время изменения записи"
    )


class DeleteFilmReviewResponse(BaseModel):
    message: str = Field(
        ..., description="Сообщение об удачном удалении ревью фильма"
    )
