import logging.config
from datetime import datetime, UTC
from functools import lru_cache
from typing import Any
from uuid import UUID

from fastapi import Depends
from pymongo import AsyncMongoClient

from src.core.logger import LOGGING
from src.core.config import settings
from src.db.mongo_client import get_mongo_client
from src.schemas.film_rating_review import FilmRatingReviewCreateUpdate, FilmRatingReviewBaseResponse
from src.utils.mongo_mixin import MongoMixin

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class RatingReviewService(MongoMixin):
    """Сервис для работы с оценкой пользовательских рецензий фильмов."""

    def __init__(self, mongo_client: AsyncMongoClient):
        self._db = mongo_client[settings.mongo_name]
        self._film_rating_reviews_collection = self._db["rating_reviews"]

    async def create(
        self,
        review_id: UUID,
        payload: dict[str | int, Any],
        rating_review_data: FilmRatingReviewCreateUpdate,
    ) -> FilmRatingReviewBaseResponse:
        """
        Добавление:
        - Оценки рецензии фильма.

        @type review_id:
        @param review_id:
        @type payload:
        @param payload:
        @type review_data:
        @param review_data:
        @rtype FilmRatingReviewBaseResponse:
        """
        rating_review_mongo_doc = {
            "review_id": str(review_id),
            "user_id": str(payload["user_id"]),
            "review_like": rating_review_data.review_like,
            "created_at": datetime.now(UTC),
        }
        rating_review_mongo_doc["_id"] = await self._insert_in_mongo(
            doc_=rating_review_mongo_doc,
            collection=self._film_rating_reviews_collection,
            log_msg=f"Create FilmRatingReview (ID={rating_review_mongo_doc['_id']})",
        )

        return FilmRatingReviewBaseResponse(**rating_review_mongo_doc)

    async def update(
        self,
        rating_review_id: UUID,
        rating_review_data: FilmRatingReviewCreateUpdate,
    ) -> FilmRatingReviewBaseResponse:
        """
        Обновление:
        - Оценки рецензии фильма.

        @type rating_review_id:
        @param rating_review_id:
        @type rating_review_data:
        @param rating_review_data:
        @rtype FilmRatingReviewBaseResponse:
        """
        film_rating_review_mongo_doc = await self._get_one_from_mongo(
            filters={"_id": rating_review_id},
            collection=self._film_rating_reviews_collection,
        )

        await self._update_in_mongo(
            collection=self._film_rating_reviews_collection,
            filters={"_id": rating_review_id},
            update_data={"review_like": rating_review_data.review_like, "modified_at": datetime.now(UTC)},
            log_msg=f"Update FilmRatingReview (ID={rating_review_id})"
        )

        return FilmRatingReviewBaseResponse(**film_rating_review_mongo_doc)

    async def delete(self, rating_review_id: UUID) -> None:
        """
        Удаление:
        - Оценки рецензии фильма.

        @type rating_review_id:
        @param rating_review_id:
        @rtype None:
        """
        await self._delete_in_mongo(
            collection=self._film_rating_reviews_collection,
            filters={"_id": rating_review_id},
            log_msg = f"Delete FilmRatingReview (ID={rating_review_id})"
        )


@lru_cache()
def get_rating_review_service(
    mongo_client=Depends(get_mongo_client)
) -> RatingReviewService:
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
    return RatingReviewService(mongo_client)
