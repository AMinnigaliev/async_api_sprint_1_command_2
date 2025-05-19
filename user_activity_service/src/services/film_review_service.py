import logging.config
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from pymongo import AsyncMongoClient

from src.core.logger import LOGGING
from src.schemas.film_review import FilmReviewResponse, BaseFilmReviewResponse

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class FilmReviewService:
    """Сервис для работы с пользовательскими рецензиями фильмов."""

    def __init__(self, mongo_client: AsyncMongoClient):
        self.mongo_client = mongo_client

    async def create_review(
        self, film_id: UUID, payload: dict, review: str
    ) -> FilmReviewResponse:
        """Добавить пользовательское ревью фильма."""
        user_id = payload.get("user_id")

        log_info = (
            f"Добавление пользовательской рецензии фильма. film_id={film_id}, "
            f"user_id={user_id} , review={review}"
        )
        logger.info(log_info)

        #  todo

    async def get_reviews(
        self, film_id: UUID, sort: str, page_size: int, page_number:int
    ) -> list[BaseFilmReviewResponse]:
        """Получить список рецензий фильма с гибкой сортировкой."""
        log_info = (
            f"Получение списка рецензий фильма. "
            f"film_id={film_id}, sort={sort}, page_size={page_size}, "
            f"page_number={page_number}"
        )
        logger.info(log_info)

        #  todo


@lru_cache()
def get_film_review_service(
    mongo_client = Depends(get_mongo_client)
) -> FilmReviewService:
    """
    Провайдер для получения экземпляра FilmReviewService.

    Функция создаёт экземпляр FilmReviewService, используя mongo_client,
    который передаётся через Depends (зависимости FastAPI).

    :param mongo_client: Экземпляр клиента MongoDB, предоставленный через
    Depends.
    :return: Экземпляр FilmReviewService, который используется для работы с
    пользовательскими рецензиями фильмов.
    """
    logger.info(
        "Создаётся экземпляр FilmReviewService с использованием MongoDB."
    )
    return FilmReviewService(mongo_client)
