from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FilmReviewCreateUpdate(BaseModel):
    review: str = Field(..., description="Текст рецензии")
    rating: int = Field(..., description="Оценка фильма пользователем")


class FilmReviewResponse(BaseModel):
    _id: str = Field(..., description="ID")
    user_id: UUID = Field(..., description="ID пользователя")
    film_id: UUID = Field(..., description="ID фильма")
    users_film_rating_id: str = Field(..., description="ID оценки фильма пользователем")
    created_at: datetime = Field(
        ..., description="Дата и время создания записи"
    )
    modified_at: datetime | None = Field(
        None, description="Дата и время изменения записи"
    )


class FilmReviewsLstResponse(BaseModel):
    total: str = Field(..., description="Общее кол-во рецензий")
    page: int = Field(..., description="Номер страницы")
    per_page: int = Field(..., description="Кол-во рецензий на странице")
    total_pages: int = Field(..., description="Общее кол-во страниц")

    film_reviews: list[FilmReviewResponse] = Field(..., description="Список рецензий фильма")


class DeleteFilmReviewResponse(BaseModel):
    message: str = Field(
        ..., description="Сообщение об удачном удалении ревью фильма"
    )
