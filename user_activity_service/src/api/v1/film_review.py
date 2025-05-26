from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.dependencies.auth import (
    role_dependency,
    role_dependency_exp_important,
)
from src.dependencies.movies import film_existence_dependency
from src.schemas.film_review import (
    DeleteFilmReviewResponse,
    FilmReviewCreateUpdate,
    FilmReviewResponse,
    FilmReviewsLstResponse,
)
from src.schemas.user_role_enum import UserRoleEnum
from src.services.film_review_service import (
    FilmReviewService,
    get_film_review_service,
)

#  Рецензия фильма
router = APIRouter()


@router.get(
    "/{film_id}",
    summary="Рецензии фильма",
    response_model=FilmReviewsLstResponse,
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
) -> FilmReviewsLstResponse:
    """
    Endpoint для получения списка рецензий с гибкой сортировкой и пагинацией.

    @type film_id:
    @param film_id:
    @type sort:
    @param sort:
    @type page_size:
    @param page_size:
    @type page_number:
    @param page_number:
    @type film_review_service:
    @param film_review_service:
    @rtype FilmReviewsLstResponse:
    """
    return await film_review_service.get(
        film_id=film_id,
        sort=sort,
        page_size=page_size,
        page_number=page_number,
    )


@router.post(
    "/{film_id}/create",
    summary="Добавить рецензию фильма",
    response_model=FilmReviewResponse,
)
async def create(
    review_data: FilmReviewCreateUpdate,
    film_id: UUID = Depends(film_existence_dependency),
    payload: dict = Depends(
        role_dependency_exp_important(UserRoleEnum.get_all_roles())
    ),
    film_review_service: FilmReviewService = Depends(get_film_review_service),
) -> FilmReviewResponse:
    """
    Endpoint для добавления ревью к фильму.

    @type review_data:
    @param review_data:
    @type film_id:
    @param film_id:
    @type payload:
    @param payload:
    @type film_review_service:
    @param film_review_service:
    @rtype FilmReviewResponse:
    """
    return await film_review_service.create(
        film_id=film_id,
        payload=payload,
        review_data=review_data
    )


@router.post(
    "/{film_review_id}/update",
    summary="Изменить рецензию фильма",
    response_model=FilmReviewResponse,
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def update(
    review_data: FilmReviewCreateUpdate,
    film_review_id: str,
    film_review_service: FilmReviewService = Depends(get_film_review_service),
) -> FilmReviewResponse:
    """
    Endpoint для обновления ревью к фильму.

    @type review_data:
    @param review_data:
    @type film_review_id:
    @param film_review_id:
    @type payload:
    @param payload:
    @type film_review_service:
    @param film_review_service:
    @rtype FilmReviewResponse:
    """
    return await film_review_service.update(
        film_review_id=film_review_id,
        review_data=review_data,
    )


@router.delete(
    "/{film_review_id}/delete",
    summary="Удалить рецензию фильма",
    response_model=DeleteFilmReviewResponse,
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def delete(
    film_review_id: str,
    film_review_service: FilmReviewService = Depends(get_film_review_service),
) -> DeleteFilmReviewResponse:
    """
    Endpoint для обновления ревью к фильму.

    @type film_review_id:
    @param film_review_id:
    @type payload:
    @param payload:
    @type film_review_service:
    @param film_review_service:
    @rtype DeleteResponse:
    """
    await film_review_service.delete(film_review_id=film_review_id)

    return DeleteFilmReviewResponse(message="Review deleted successfully")
