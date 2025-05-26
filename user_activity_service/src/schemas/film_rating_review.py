from datetime import datetime

from pydantic import BaseModel, Field


class FilmRatingReviewCreateUpdate(BaseModel):
    review_like: bool = Field(..., description="Понравилась рецензия или нет")


class FilmRatingReviewBaseResponse(FilmRatingReviewCreateUpdate):
    id: str = Field(..., description="ID")
    user_id: str = Field(..., description="ID пользователя")
    review_id: str = Field(..., description="ID рецензии")
    created_at: datetime = Field(
        ..., description="Дата и время создания записи"
    )


class DeleteRatingReviewResponse(BaseModel):
    message: str = Field(..., description="Оповещение о статусе удаления")
    rating_review_id: str = Field(..., description="ID оценки рецензии")
