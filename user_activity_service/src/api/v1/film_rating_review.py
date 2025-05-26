from fastapi import APIRouter, Depends

from src.dependencies.auth import (
    role_dependency,
    role_dependency_exp_important,
)
from src.schemas.film_rating_review import (
    DeleteRatingReviewResponse,
    FilmRatingReviewBaseResponse,
    FilmRatingReviewCreateUpdate,
)
from src.schemas.user_role_enum import UserRoleEnum
from src.services.film_rating_review_service import (
    RatingReviewService,
    get_rating_review_service,
)

#  Оценка рецензии фильма
router = APIRouter()


@router.post(
    "/{review_id}",
    summary="Добавить оценку рецензии фильма",
    response_model=FilmRatingReviewBaseResponse,
)
async def create(
    rating_review_data: FilmRatingReviewCreateUpdate,
    review_id: str,
    payload: dict = Depends(role_dependency_exp_important(
        UserRoleEnum.get_all_roles())
    ),
    rating_review_service: RatingReviewService = Depends(
        get_rating_review_service
    ),
) -> FilmRatingReviewBaseResponse:
    """
    Endpoint для добавления оценки рецензии фильма.

    @type review_like_data:
    @param review_like_data:
    @type review_id:
    @param review_id:
    @type payload:
    @param payload:
    @type review_rating_service:
    @param review_rating_service:
    @rtype FilmRatingReviewBaseResponse:
    """
    return await rating_review_service.create(
        rating_review_data=rating_review_data,
        review_id=review_id,
        payload=payload,
    )


@router.post(
    "/{rating_review_id}/update",
    summary="Изменить оценку рецензии фильма",
    response_model=FilmRatingReviewBaseResponse,
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def update(
    rating_review_data: FilmRatingReviewCreateUpdate,
    rating_review_id: str,
    rating_review_service: RatingReviewService = Depends(
        get_rating_review_service
    ),
) -> FilmRatingReviewBaseResponse:
    """
    Endpoint для изменения оценки рецензии фильма.

    @type rating_review_data:
    @param rating_review_data:
    @type rating_review_id:
    @param rating_review_id:
    @type payload:
    @param payload:
    @type review_rating_service:
    @param review_rating_service:
    @rtype FilmRatingReviewBaseResponse:
    """
    return await rating_review_service.update(
        rating_review_data=rating_review_data,
        rating_review_id=rating_review_id,
    )


@router.delete(
    "/{rating_review_id}",
    summary="Удалить оценку рецензии фильма",
    response_model=DeleteRatingReviewResponse,
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def delete(
    rating_review_id: str,
    rating_review_service: RatingReviewService = Depends(
        get_rating_review_service
    ),
) -> DeleteRatingReviewResponse:
    """
    Endpoint для удаления оценки рецензии фильма.

    @type rating_review_id:
    @param rating_review_id:
    @type review_rating_service:
    @param review_rating_service:
    @rtype DeleteRatingReviewResponse:
    """
    await rating_review_service.delete(rating_review_id=rating_review_id)

    return DeleteRatingReviewResponse(
        message="Review rating deleted successfully",
        rating_review_id=rating_review_id,
    )
