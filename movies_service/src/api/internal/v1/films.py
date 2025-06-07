import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.models import Film, FilmBase, SearchParams
from src.services.internal_film_service import FilmService, get_film_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/search",
    response_model=list[FilmBase],
)
async def search_films(
    search_params: SearchParams,
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Количество записей в результате (от 1 до 100)",
    ),
    page_number: int = Query(
        1,
        ge=1,
        description="Смещение для пагинации (больше ноля)",
    ),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBase]:
    films = await film_service.search_films(search_params=search_params, page_size=page_size, page_number=page_number)

    return films if films else []