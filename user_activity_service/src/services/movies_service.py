import asyncio
import json
import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status

from src.core.config import settings
from src.core.exceptions import CacheServiceError
from src.db.redis_client import get_redis_cache
from src.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class MoviesService:
    def __init__(self, redis_client: CacheService):
        self.redis_client = redis_client

    @staticmethod
    async def verify_film_through_movies(
        film_id: UUID, request_id: str
    ) -> dict:
        """Проверяет фильма через movies-сервис."""
        headers = {
            "X-Request-Id": request_id,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.movies_service_url}/is_exist/{film_id}",
                    headers=headers,
                    timeout=1.0,
                )
                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Ошибка при проверки фильма через movies-сервис: %s "
                    "film_id=%s",
                    e, film_id
                )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail="Film not exist"
                )

            except httpx.RequestError:
                logger.error(
                    "Movies-сервис недоступен для проверки фильма, "
                    "film_id=%s ",
                    film_id
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Movies service unavailable"
                )

        return response.json()

    async def varify_film_with_cache(
        self, film_id: UUID, request_id: str
    ) -> dict:
        """Проверяет фильм с использованием кеша через movies-сервис."""
        cache_key = f"film_id:{film_id}"

        message = (
            f"Проверяем наличие информации о существовании фильма в кеше: "
            f"key={cache_key}"
        )
        logger.info(message)

        try:
            if cached := await self.redis_client.get(cache_key, message):
                logger.info(
                    "Информация о существовании фильма найдена в кеше: "
                    "key=%s value=%s",
                    cache_key, cached
                )
                try:
                    return json.loads(cached)

                except json.JSONDecodeError as e:
                    logger.error(
                        "Ошибка декодирования значения из кеша для информации "
                        "о наличии фильма: %s key=%s value=%s",
                        e, cache_key, cached
                    )
        except CacheServiceError:
            pass

        is_film_exist = await self.verify_film_through_movies(
            film_id, request_id
        )

        asyncio.create_task(self.redis_client.set(
            cache_key, json.dumps(is_film_exist),
        ))

        return is_film_exist


@lru_cache()
def get_movies_service(
    redis: Annotated[CacheService, Depends(get_redis_cache)],
) -> MoviesService:
    """
    Провайдер для получения экземпляра MoviesService.

    Функция создаёт синглтон экземпляр MoviesService, используя Redis,
    который передаётся через Depends (зависимости FastAPI).

    :param redis: Экземпляр клиента Redis, предоставленный через Depends.
    :return: Экземпляр MoviesService, который используется для
    проверки существования фильма.
    """
    logger.info(
        "Создаётся экземпляр MoviesService с использованием Redis."
    )
    return MoviesService(redis)
