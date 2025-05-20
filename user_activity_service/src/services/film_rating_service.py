import logging.config
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from pymongo import AsyncMongoClient

from src.core.logger import LOGGING
from src.db.mongo_client import get_mongo_client
from src.schemas.film_rating import (AmountFilmRatingResponse,
                                     AverageFilmRatingResponse,
                                     FilmRatingResponse)

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class FilmRatingService:
    """Сервис для работы с пользовательскими оценками фильмов."""

    def __init__(self, mongo_client: AsyncMongoClient):
        self.mongo_client = mongo_client

    async def average(self, film_id: UUID) -> AverageFilmRatingResponse:
        """Получить среднюю пользовательскую оценку фильма по его ID."""
        log_info = (
            f"Получение средней пользовательской оценки фильма по ID {film_id}"
        )
        logger.info(log_info)

        #  todo

    async def amount(self, film_id: UUID) -> AmountFilmRatingResponse:
        """Получить количество пользовательских оценок фильма по его ID."""
        log_info = (
            f"Получение количество пользовательских оценок фильма по "
            f"ID {film_id}"
        )
        logger.info(log_info)

        #  todo

    async def create(
        self, film_id: UUID, payload: dict, rating: int
    ) -> FilmRatingResponse:
        """Добавить пользовательскую оценку фильма."""
        user_id = payload.get("user_id")

        log_info = (
            f"Добавление пользовательской оценки фильма. film_id={film_id}, "
            f"user_id={user_id} , rating={rating}"
        )
        logger.info(log_info)

        #  todo

    async def update(
        self, rating_id: UUID, payload: dict, new_rating: int
    ) -> FilmRatingResponse:
        """Изменить пользовательскую оценку фильма."""
        user_id = payload.get("user_id")

        log_info = (
            f"Изменение пользовательской оценки фильма. "
            f"rating_id={rating_id}, user_id={user_id}, "
            f"new_rating={new_rating}"
        )
        logger.info(log_info)

        #  todo

    async def delete(self, rating_id: UUID, payload: dict) -> None:
        """Удалить пользовательскую оценку фильма."""
        user_id = payload.get("user_id")

        log_info = (
            f"Удаление пользовательской оценки фильма. "
            f"rating_id={rating_id}, user_id={user_id}"
        )
        logger.info(log_info)

        #  todo


@lru_cache()
def get_film_rating_service(
    mongo_client=Depends(get_mongo_client)
) -> FilmRatingService:
    """
    Провайдер для получения экземпляра FilmRatingService.

    Функция создаёт экземпляр FilmRatingService, используя mongo_client,
    который передаётся через Depends (зависимости FastAPI).

    :param mongo_client: Экземпляр клиента MongoDB, предоставленный через
    Depends.
    :return: Экземпляр FilmRatingService, который используется для работы с
    пользовательскими оценками фильмов.
    """
    logger.info(
        "Создаётся экземпляр FilmRatingService с использованием MongoDB."
    )
    return FilmRatingService(mongo_client)
