from uuid import UUID

from bson import ObjectId
from fastapi import APIRouter, Depends

from src.dependencies.auth import (role_dependency,
                                   role_dependency_exp_important)
from src.dependencies.movies import film_existence_dependency
from src.schemas.film_rating import (DeleteFilmRatingResponse,
                                     FilmRatingCreateUpdate,
                                     FilmRatingResponse,
                                     AmtAvgFilmRatingResponse)
from src.schemas.user_role_enum import UserRoleEnum
from src.services.film_rating_service import (FilmRatingService,
                                              get_film_rating_service)

router = APIRouter()


@router.get(
    "/{film_id}/amt-avg",
    summary="Количество и средний рейтинг пользовательских оценок фильма",
    response_model=AmtAvgFilmRatingResponse,
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def amt_avg_rating(
    film_id: UUID = Depends(film_existence_dependency),
    film_rating_service: FilmRatingService = Depends(get_film_rating_service),
) -> AmtAvgFilmRatingResponse:
    """
    Эндпоинт для получения количества и среднего рейтинга пользовательских
    оценок фильма.
    """
    return await film_rating_service.amt_avg(film_id)


@router.post(
    "/{film_id}/create",
    summary="Добавить оценку фильму",
    response_model=FilmRatingResponse,
)
async def create_rating(
    rating_data: FilmRatingCreateUpdate,
    film_id: UUID = Depends(film_existence_dependency),
    payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    film_rating_service: FilmRatingService = Depends(get_film_rating_service),
) -> FilmRatingResponse:
    """Эндпоинт для добавления пользовательской оценки фильма."""
    rating = rating_data.rating
    return await film_rating_service.create(film_id, payload, rating)


@router.post(
    "/{rating_id}/update",
    summary="Изменить пользовательскую оценку фильма",
    response_model=FilmRatingResponse,
)
async def update_rating(
    rating_data: FilmRatingCreateUpdate,
    rating_id: ObjectId,
    payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    film_rating_service: FilmRatingService = Depends(get_film_rating_service),
) -> FilmRatingResponse:
    """Эндпоинт для изменения пользовательской оценки фильма."""
    new_rating = rating_data.rating
    return await film_rating_service.update(
        rating_id, payload, new_rating
    )


@router.delete(
    "/{rating_id}/delete",
    summary="Удалить пользовательскую оценку фильма",
    response_model=DeleteFilmRatingResponse,
)
async def delete_rating(
    rating_id: ObjectId,
    payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    film_rating_service: FilmRatingService = Depends(get_film_rating_service),
) -> DeleteFilmRatingResponse:
    """Эндпоинт для удаления пользовательской оценки фильма."""
    await film_rating_service.delete(rating_id, payload)
    return DeleteFilmRatingResponse(message="Rating deleted successfully")
