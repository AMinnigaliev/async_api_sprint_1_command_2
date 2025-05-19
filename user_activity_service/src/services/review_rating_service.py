import logging.config
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from pymongo import AsyncMongoClient

from src.core.logger import LOGGING
from src.schemas.film_review import FilmReviewResponse, BaseFilmReviewResponse

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class ReviewRatingService:
    """Сервис для работы с лайками пользовательских рецензий фильмов."""

    def __init__(self, mongo_client: AsyncMongoClient):
        self.mongo_client = mongo_client

    async def create(
        self, review_id: UUID, payload: dict, review_like: str
    ) -> FilmReviewResponse:
        """Добавить оценку пользовательскому ревью фильма."""
        user_id = payload.get("user_id")

        log_info = (
            f"Добавление оценки пользовательской рецензии фильма. "
            f"review_id={review_id}, user_id={user_id}, "
            f"review_like={review_like}"
        )
        logger.info(log_info)

        #  todo


@lru_cache()
def get_review_rating_service(
    mongo_client = Depends(get_mongo_client)
) -> ReviewRatingService:
    """
    Провайдер для получения экземпляра ReviewRatingService.

    Функция создаёт экземпляр ReviewRatingService, используя mongo_client,
    который передаётся через Depends (зависимости FastAPI).

    :param mongo_client: Экземпляр клиента MongoDB, предоставленный через
    Depends.
    :return: Экземпляр ReviewRatingService, который используется для работы с
    лайками пользовательских рецензий фильмов.
    """
    logger.info(
        "Создаётся экземпляр ReviewRatingService с использованием MongoDB."
    )
    return ReviewRatingService(mongo_client)
