from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.dependencies.request import get_request_id
from src.services.movies_service import MoviesService, get_movies_service


async def film_existence_dependency(
    film_id: UUID,
    request_id: str = Depends(get_request_id),
    movies_service: MoviesService = Depends(get_movies_service),
) -> UUID:
    if not await movies_service.varify_film_with_cache(film_id, request_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Film not found")

    return film_id
