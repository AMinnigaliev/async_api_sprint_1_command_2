from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FilmRatingReviewCreateUpdate(BaseModel):
    review_id: UUID = Field(..., description="ID рецензии")
    review_like: bool = Field(..., description="Понравилась рецензия или нет")


class FilmRatingReviewBaseResponse(BaseModel):
    _id: str = Field(..., description="ID")

    user_id: UUID = Field(..., description="ID пользователя")
    review_id: UUID = Field(..., description="ID рецензии")
    review_like: bool = Field(..., description="Понравилась рецензия или нет")
    created_at: datetime = Field(
        ..., description="Дата и время создания записи"
    )


class DeleteRatingReviewResponse(BaseModel):
    message: str = Field(..., description="Оповещение о статусе удаления")
