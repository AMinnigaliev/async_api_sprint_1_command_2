import logging.config
from datetime import datetime, UTC
from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError

from src.core.config import settings
from src.core.logger import LOGGING
from src.db.mongo_client import get_mongo_client
from src.schemas.film_rating import (FilmRatingResponse,
                                     AmtAvgFilmRatingResponse,
                                     DeleteFilmRatingResponse)

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class FilmRatingService:
    """Сервис для работы с пользовательскими оценками фильмов."""

    def __init__(self, mongo_client: AsyncMongoClient):
        db = mongo_client[settings.mongo_name]
        self.collection_ratings = db["film_ratings"]
        self.collection_overall = db["overall_film_ratings"]

    async def _recalc_overall(self, film_id: UUID) -> None:
        """
        Пересчитать и записать в collection_overall количество и
        средний рейтинг.
        """
        logger.info(
            "Вычисление количества и среднего рейтинга пользовательских "
            "оценок фильма по ID %s",
            film_id,
        )
        cursor = self.collection_ratings.find({"film_id": film_id})
        total = 0
        count = 0
        async for doc in cursor:
            total += doc["rating"]
            count += 1

        now = datetime.now(UTC)

        logger.info(
            "Обновление количества и среднего рейтинга пользовательских "
            "оценок фильма по ID %s",
            film_id,
        )
        if count == 0:
            # если больше нет оценок — удаляем агрегат
            await self.collection_overall.delete_one({"film_id": film_id})

        else:
            avg = total / count
            await self.collection_overall.update_one(
                {"film_id": film_id},
                {
                    "$set": {
                        "amount_ratings": count,
                        "average_rating": avg,
                        "modified_at": now,
                    },
                    "$setOnInsert": {
                        "film_id": film_id,
                        "created_at": now,
                    },
                },
                upsert=True,
            )

    async def amt_avg(self, film_id: UUID) -> AmtAvgFilmRatingResponse:
        """
        Получить количество и средний рейтинг пользовательских оценок фильма
        по его ID.
        """
        logger.info(
            "Получение количества и среднего рейтинга пользовательских оценок "
            "фильма по ID %s",
            film_id,
        )
        doc = await self.collection_overall.find_one({"film_id": film_id})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There are no ratings for this movie {film_id} yet."
            )
        return AmtAvgFilmRatingResponse(**doc)

    async def create(
        self, film_id: UUID, payload: dict, rating: int
    ) -> FilmRatingResponse:
        """Добавить пользовательскую оценку фильма."""
        user_id = payload.get("user_id")

        logger.info(
            "Добавление пользовательской оценки фильма. "
            "film_id=%s, user_id=%s, rating=%s",
            film_id, user_id, rating
        )

        now = datetime.now(UTC)
        doc = {
            "film_id": film_id,
            "user_id": user_id,
            "rating": rating,
            "created_at": now,
        }
        try:
            result = await self.collection_ratings.insert_one(doc)
            doc["_id"] = result.inserted_id

        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A rating for this movie from the user already exists",
            )

        # пересчёт overall
        await self._recalc_overall(film_id)

        return FilmRatingResponse(**doc)

    async def update(
        self, rating_id: UUID, payload: dict, new_rating: int
    ) -> FilmRatingResponse:
        """Изменить пользовательскую оценку фильма."""
        user_id = payload.get("user_id")

        logger.info(
            "Изменение пользовательской оценки фильма. "
            "rating_id=%s, user_id=%s, new_rating=%s",
            rating_id, user_id, new_rating
        )

        now = datetime.now(UTC)

        existing = await self.collection_ratings.find_one(
            {"_id": rating_id, "user_id": user_id}
        )
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found or does not belong to the user",
            )

        film_id = existing.get("film_id")

        await self.collection_ratings.update_one(
            {"_id": rating_id, "user_id": user_id},
            {"$set": {"rating": new_rating, "modified_at": now}},
        )

        # пересчёт агрегатов
        await self._recalc_overall(film_id)

        return FilmRatingResponse(
            _id=rating_id,
            film_id=film_id,
            user_id=user_id,
            rating=new_rating,
            created_at=existing["created_at"],
            modified_at=now,
        )

    async def delete(self, rating_id: UUID, payload: dict) -> None:
        """Удалить пользовательскую оценку фильма."""
        user_id = payload.get("user_id")

        log_info = (
            f"Удаление пользовательской оценки фильма. "
            f"rating_id={rating_id}, user_id={user_id}"
        )
        logger.info(log_info)

        existing = await self.collection_ratings.find_one(
            {"_id": rating_id, "user_id": user_id}
        )
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found or does not belong to the user",
            )

        await self.collection_ratings.delete_one(
            {"_id": rating_id, "user_id": user_id}
        )

        await self._recalc_overall(existing["film_id"])

        return DeleteFilmRatingResponse(message="Rating deleted successfully")

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
