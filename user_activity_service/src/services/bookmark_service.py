import logging.config
from datetime import UTC, datetime
from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError

from src.core.config import settings
from src.core.logger import LOGGING
from src.db.mongo_client import get_mongo_client
from src.schemas.bookmark import BookmarkResponse
from src.utils.object_id_converter import get_object_id, get_string_id

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class BookmarkService:
    """Сервис для работы с пользовательскими закладками на фильмы."""

    def __init__(self, mongo_client: AsyncMongoClient):
        self.collection = mongo_client[settings.mongo_name]["bookmarks"]

    async def create(self, film_id: UUID, payload: dict) -> BookmarkResponse:
        """Добавить пользовательскую закладку на фильм."""
        user_id = payload.get("user_id")
        film_id = str(film_id)

        logger.info(
            "Добавление пользовательской закладки на фильм. "
            "film_id=%s, user_id=%s",
            film_id, user_id
        )

        existing = await self.collection.find_one(
            {"user_id": user_id, "film_id": film_id}
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bookmark already exists",
            )

        doc = {
            "user_id": user_id,
            "film_id": film_id,
            "created_at": datetime.now(UTC),
        }

        try:
            result = await self.collection.insert_one(doc)
            _id = result.inserted_id
            doc["bookmark_id"] = get_string_id(_id)

        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bookmark already exists",
            )

        return BookmarkResponse(**doc)

    async def delete(self, bookmark_id: str, payload: dict) -> None:
        """Удалить пользовательскую закладку на фильм."""
        user_id = payload.get("user_id")

        logger.info(
            "Удаление пользовательской закладки на фильм. "
            "bookmark_id=%s, user_id=%s",
            bookmark_id, user_id
        )

        _id = get_object_id(bookmark_id)
        result = await self.collection.delete_one({
            "_id": _id, "user_id": user_id
        })
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found or no rights to delete"
            )

    async def get_bookmarks(self, payload: dict) -> list[BookmarkResponse]:
        """Получить список рецензий фильма с гибкой сортировкой."""
        user_id = payload.get("user_id")

        logger.info("Получение списка закладок на фильмы. user_id=%s", user_id)

        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1)

        docs = await cursor.to_list(length=None)
        return [
            BookmarkResponse(
                bookmark_id=get_string_id(doc["_id"]),
                user_id=doc["user_id"],
                film_id=doc["film_id"],
                created_at=doc["created_at"],
            )
            for doc in docs
        ]


@lru_cache()
def get_bookmark_service(
    mongo_client=Depends(get_mongo_client)
) -> BookmarkService:
    """
    Провайдер для получения экземпляра BookmarkService.

    Функция создаёт экземпляр BookmarkService, используя mongo_client,
    который передаётся через Depends (зависимости FastAPI).

    :param mongo_client: Экземпляр клиента MongoDB, предоставленный через
    Depends.
    :return: Экземпляр BookmarkService, который используется для работы с
    пользовательскими закладками на фильмы.
    """
    logger.info(
        "Создаётся экземпляр BookmarkService с использованием MongoDB."
    )
    return BookmarkService(mongo_client)
