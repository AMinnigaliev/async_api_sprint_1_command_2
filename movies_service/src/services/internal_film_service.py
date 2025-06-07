import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from src.db.elastic import get_elastic
from src.db.redis_client import get_redis_cache
from src.models.models import Film, FilmBase
from src.services.base_service import BaseService
from src.utils.cache_service import CacheService
from src.utils.elastic_service import ElasticService

logger = logging.getLogger(__name__)


class FilmService(BaseService):

    async def search_films(
        self,
        search_params,
        page_size: int = 10,
        page_number: int = 1,
    ) -> list[BaseModel] | None:
        """
        Поиск фильмов по ключевым словам и пагинацией.
        """
        log_info = (
            f"Запрос на получение фильмов: params={search_params}, page_size={page_size}, page_number={page_number}"
        )

        es_index = "film_work"
        model = FilmBase
        body = {"query": {}, "from": (page_number - 1) * page_size, "size": page_size}

        if query := search_params.query:
            body["query"] = query

        else:
            body["query"]["match_all"] = {}

        if sort := search_params.sort:
            body["sort"] = sort

        return await self._base_get_no_cache(model, es_index, body, log_info)


@lru_cache()
def get_film_service(
    redis: Annotated[CacheService, Depends(get_redis_cache)],
    elastic: Annotated[ElasticService, Depends(get_elastic)]
) -> FilmService:
    return FilmService(redis, elastic)
