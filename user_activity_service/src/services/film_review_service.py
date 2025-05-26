import logging.config
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any
from uuid import UUID

from fastapi import Depends
from pymongo import AsyncMongoClient

from src.core.config import settings
from src.core.logger import LOGGING
from src.db.mongo_client import get_mongo_client
from src.schemas.film_review import (FilmReviewCreateUpdate,
                                     FilmReviewResponse,
                                     FilmReviewsLstResponse)
from src.utils.mongo_mixin import MongoMixin

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class FilmReviewService(MongoMixin):
    """Сервис для работы с пользовательскими рецензиями фильмов."""

    def __init__(self, mongo_client: AsyncMongoClient):
        self._db = mongo_client[settings.mongo_name]
        self._film_ratings_collection = self._db["film_ratings"]
        self._film_reviews_collection = self._db["film_reviews"]

    async def get(
        self,
        film_id: UUID,
        sort: str,
        page_size: int,
        page_number: int,
    ) -> FilmReviewsLstResponse:
        """
        Получение списка:
        - Ревью к фильму.

        @type film_id:
        @param film_id:
        @type sort:
        @param sort:
        @type page_size:
        @param page_size:
        @type page_number:
        @param page_number:
        @rtype FilmReviewsLstResponse:
        """
        filters = {"film_id": film_id}

        data = await self._get_collection_docs_with_pagination(
            collection=self._film_reviews_collection,
            filters=filters,
            skip=(page_number - 1) * page_size,
            sort_field=sort,
            per_page=page_size,
        )
        docs_lst = list(data) if data else []

        total = await self._get_count_documents(collection=self._film_reviews_collection, filters=filters)
        total_pages = (total + page_size - 1) // page_size

        response_ = FilmReviewsLstResponse(
            total=total,
            page=page_number,
            per_page=page_size,
            total_pages=total_pages,
            film_reviews=[FilmReviewResponse(**doc) for doc in docs_lst],
        )

        return response_

    async def create(
        self,
        film_id: UUID,
        payload: dict[str | int, Any],
        review_data: FilmReviewCreateUpdate,
    ) -> FilmReviewResponse:
        """
        Добавление:
        - Оценки фильма.
        - Ревью к фильму с оценкой к фильму.

        @type film_id:
        @param film_id:
        @type payload:
        @param payload:
        @type review_data:
        @param review_data:
        @rtype FilmReviewResponse:
        """
        now = datetime.now(UTC)
        user_id = str(payload["user_id"])

        film_rating_mongo_doc = {
            "film_id": str(film_id),
            "user_id": user_id,
            "rating": review_data.rating,
            "created_at": now,
        }
        film_rating_mongo_doc["_id"] = await self._insert_in_mongo(
            doc_=film_rating_mongo_doc,
            collection=self._film_ratings_collection,
            log_msg=f"Create FilmRating (FilnID={film_id}, UserID={user_id})",
        )

        film_review_mongo_doc = {
            "users_film_rating_id": film_rating_mongo_doc["_id"],
            "user_id": user_id,
            "film_id": str(film_id),
            "review": review_data.review,
            "created_at": now,
            "modified_at": now,
        }
        film_review_mongo_doc["_id"] = await self._insert_in_mongo(
            doc_=film_review_mongo_doc,
            collection=self._film_reviews_collection,
            log_msg=f"Create FilmReview (FilmID={film_id}, UserID={user_id})",
        )

        return FilmReviewResponse(**film_review_mongo_doc)

    async def update(self, film_review_id: UUID, review_data: FilmReviewCreateUpdate) -> FilmReviewResponse:
        """
        Обновление:
        - Оценки фильма.
        - Ревью к фильму с оценкой к фильму.

        @type film_review_id:
        @param film_review_id:
        @type review_data:
        @param review_data:
        @rtype FilmReviewResponse:
        """
        now = datetime.now(UTC)
        await self._update_in_mongo(
            collection=self._film_reviews_collection,
            filters={"_id": film_review_id},
            update_data={"review": review_data.review, "modified_at": now},
            log_msg=f"Update FilmReview (ID={film_review_id})"
        )

        film_review_mongo_doc = await self._get_one_from_mongo(
            filters={"_id": film_review_id},
            collection=self._film_reviews_collection,
        )
        if users_film_rating_id := film_review_mongo_doc.get("users_film_rating_id"):
            await self._update_in_mongo(
                collection=self._film_ratings_collection,
                filters={"_id": users_film_rating_id},
                update_data={"rating": review_data.rating, "modified_at": now},
                log_msg = f"Update FilmRating (ID={users_film_rating_id})"
            )

        return FilmReviewResponse(**film_review_mongo_doc)

    async def delete(self, film_review_id: UUID) -> None:
        """
        Удаление:
        - Оценки фильма.
        - Ревью к фильму с оценкой к фильму.

        @type film_review_id:
        @param film_review_id:
        @type payload:
        @param payload:
        @rtype None:
        """
        film_review_mongo_doc = await self._get_one_from_mongo(
            filters={"_id": film_review_id},
            collection=self._film_reviews_collection,
        )

        if users_film_rating_id := film_review_mongo_doc.get("users_film_rating_id"):
            await self._delete_in_mongo(
                collection=self._film_ratings_collection,
                filters={"_id": users_film_rating_id},
                log_msg = f"Delete FilmRating (ID={users_film_rating_id})"
            )

        await self._delete_in_mongo(
            collection=self._film_reviews_collection,
            filters={"_id": film_review_id},
            log_msg = f"Delete FilmReview (ID={film_review_id})"
        )


@lru_cache()
def get_film_review_service(
    mongo_client=Depends(get_mongo_client),
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
        "Создаётся экземпляр FilmReviewService с использованием MongoDB",
    )
    return FilmReviewService(mongo_client)
