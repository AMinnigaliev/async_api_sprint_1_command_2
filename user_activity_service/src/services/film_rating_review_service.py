import logging.config
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

from bson import ObjectId
from fastapi import Depends
from pymongo import AsyncMongoClient

from src.core.config import settings
from src.core.logger import LOGGING
from src.db.mongo_client import get_mongo_client
from src.schemas.film_rating_review import (FilmRatingReviewBaseResponse,
                                            FilmRatingReviewCreateUpdate)
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
        review_id: str,
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
            "review_id": review_id,
            "user_id": payload["user_id"],
            "review_like": rating_review_data.review_like,
            "created_at": datetime.now(UTC),
        }
        rating_review_mongo_doc["_id"] = await self._insert_in_mongo(
            doc_=rating_review_mongo_doc,
            collection=self._film_rating_reviews_collection,
            log_msg=f"Create FilmRatingReview (ReviewID={review_id})",
        )

        return FilmRatingReviewBaseResponse(
            id=str(rating_review_mongo_doc["_id"]),
            review_id=review_id,
            user_id=rating_review_mongo_doc["user_id"],
            review_like=rating_review_mongo_doc["review_like"],
            created_at=rating_review_mongo_doc["created_at"],
        )

    async def update(
        self,
        rating_review_id: str,
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
        await self._update_in_mongo(
            collection=self._film_rating_reviews_collection,
            filters={"_id": ObjectId(rating_review_id)},
            update_data={
                "review_like": rating_review_data.review_like,
                "modified_at": datetime.now(UTC),
            },
            log_msg=f"Update FilmRatingReview (ID={rating_review_id})"
        )

        rating_review_mongo_doc = await self._get_one_from_mongo(
            filters={
                "_id": ObjectId(rating_review_id),
            },
            collection=self._film_rating_reviews_collection,
        )

        return FilmRatingReviewBaseResponse(
            id=str(rating_review_mongo_doc["_id"]),
            review_id=rating_review_mongo_doc["review_id"],
            user_id=rating_review_mongo_doc["user_id"],
            review_like=rating_review_mongo_doc["review_like"],
            created_at=rating_review_mongo_doc["created_at"],
        )

    async def delete(self, rating_review_id: str) -> None:
        """
        Удаление:
        - Оценки рецензии фильма.

        @type rating_review_id:
        @param rating_review_id:
        @rtype None:
        """
        await self._delete_in_mongo(
            collection=self._film_rating_reviews_collection,
            filters={"_id": ObjectId(rating_review_id)},
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
