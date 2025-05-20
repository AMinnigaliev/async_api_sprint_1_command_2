from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.dependencies.auth import (role_dependency,
                                   role_dependency_exp_important)
from src.dependencies.movies import film_existence_dependency
from src.schemas.film_review import (BaseFilmReviewResponse,
                                     FilmReviewCreateUpdate,
                                     FilmReviewResponse,
                                     ReviewRatingCreateUpdate,
                                     ReviewRatingResponse)
from src.schemas.user_role_enum import UserRoleEnum
from src.services.film_review_service import (FilmReviewService,
                                              get_film_review_service)
from src.services.review_rating_service import (ReviewRatingService,
                                                get_review_rating_service)

router = APIRouter()


@router.post(
    "/{film_id}/create",
    summary="Добавить рецензию фильма",
    response_model=FilmReviewResponse,
)
async def create_review(
    review_data: FilmReviewCreateUpdate,
    film_id: UUID = Depends(film_existence_dependency),
    payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    film_review_service: FilmReviewService = Depends(get_film_review_service),
) -> FilmReviewResponse:
    """Эндпоинт для добавления ревью фильму."""
    review = review_data.review
    return await film_review_service.create(film_id, payload, review)


@router.get(
    "/{film_id}",
    summary="Рецензии фильма",
    response_model=list[BaseFilmReviewResponse],
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def list_reviews(
    film_id: UUID,
    sort: str = Query(
        "-created",
        description="Поле для сортировки (например, '-created')",
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Количество рецензий в результате (от 1 до 100)",
    ),
    page_number: int = Query(
        1,
        ge=1,
        description="Смещение для пагинации (больше ноля)",
    ),
    film_review_service: FilmReviewService = Depends(get_film_review_service),
) -> list[BaseFilmReviewResponse]:
    """Эндпоинт для получения списка рецензий с гибкой сортировкой"""
    return await film_review_service.get_reviews(
        film_id, sort, page_size, page_number
    )


@router.post(
    "/{review_id}/rating/create",
    summary="Добавить оценку рецензии фильма",
    response_model=ReviewRatingResponse,
)
async def create_review_rating(
    review_like_data: ReviewRatingCreateUpdate,
    review_id: UUID,
    payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    review_rating_service: ReviewRatingService = Depends(
        get_review_rating_service
    ),
) -> ReviewRatingResponse:
    """Эндпоинт для добавления оценки рецензии фильма."""
    review_like = review_like_data.review_like
    return await review_rating_service.create(
        review_id, payload, review_like
    )


# @router.post(
#     "/review-rating/{review_rating_id}/update",
#     summary="Изменить оценку рецензии фильма",
#     response_model=FilmReviewResponse,
# )
# async def update_review_rating(
#     new_review_like: ReviewRatingCreateUpdate,
#     review_rating_id: UUID,
#     payload: dict = Depends(role_dependency(UserRoleEnum.get_all_roles())),
#     review_rating_service: ReviewRatingService = Depends(
#         get_review_rating_service
#     ),
# ) -> FilmReviewResponse:
#     """Эндпоинт для изменения оценки рецензии фильма."""
#     return await review_rating_service.update(
#         review_rating_id, payload, new_review_like
#     )
#
# @router.delete(
#     "/review-rating/{review_rating_id}/delete",
#     summary="Удалить оценку рецензии фильма",
#     response_model=DeleteFilmReviewResponse,
# )
# async def delete(
#     review_rating_id: UUID,
#     payload: dict = Depends(role_dependency(UserRoleEnum.get_all_roles())),
#     review_rating_service: ReviewRatingService = Depends(
#         get_review_rating_service
#     ),
# )-> DeleteFilmReviewResponse:
#     """Эндпоинт для удаления оценки рецензии фильма."""
#     await review_rating_service.delete(review_rating_id, payload)
#     return DeleteFilmReviewResponse(message="Review rating deleted successfully")


# @router.post(
#     "/review/{film_rating_id}/update",
#     summary="Изменить рецензию фильма",
#     response_model=FilmReviewResponse,
# )
# async def update(
#     new_review: FilmReviewCreateUpdate,
#     film_rating_id: UUID,
#     payload: dict = Depends(role_dependency(UserRoleEnum.get_all_roles())),
#     film_review_service: FilmReviewService = Depends(get_film_review_service),
# ) -> FilmReviewResponse:
#     """Эндпоинт для изменения рецензии фильма."""
#     return await film_review_service.update(
#         film_id, payload, new_review
#     )
#
#
# @router.delete(
#     "/rating/{film_rating_id}/delete",
#     summary="Удалить рецензию фильма",
#     response_model=DeleteResponse,
# )
# async def delete(
#     film_rating_id: UUID,
#     payload: dict = Depends(role_dependency(UserRoleEnum.get_all_roles())),
#     film_review_service: FilmReviewService = Depends(get_film_review_service),
# ) -> DeleteResponse:
#     """Эндпоинт для удаления рецензии фильма."""
#     await film_review_service.delete(film_rating_id, payload)
#     return DeleteResponse(message="Review deleted successfully")
