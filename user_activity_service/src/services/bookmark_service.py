import logging.config
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from pymongo import AsyncMongoClient

from src.core.logger import LOGGING
from src.db.mongo_client import get_mongo_client
from src.schemas.bookmark import BookmarkResponse

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class BookmarkService:
    """Сервис для работы с пользовательскими закладками на фильмы."""

    def __init__(self, mongo_client: AsyncMongoClient):
        self.mongo_client = mongo_client
        self.collection = self.mongo_client["your_db_name"]["bookmark"]

    async def create(self, film_id: UUID, payload: dict) -> BookmarkResponse:
        """Добавить пользовательскую закладку на фильм."""
        user_id = payload.get("user_id")

        log_info = (
            f"Добавление пользовательской закладки на фильм. "
            f"film_id={film_id}, user_id={user_id}"
        )
        logger.info(log_info)

        #  todo

    async def delete(self, film_id: UUID, payload: dict) -> None:
        """Удалить пользовательскую закладку на фильм."""
        user_id = payload.get("user_id")

        log_info = (
            f"Удаление пользовательской закладки на фильм. "
            f"film_id={film_id}, user_id={user_id}"
        )
        logger.info(log_info)

        #  todo

    async def get_bookmarks(self, payload: dict) -> list[BookmarkResponse]:
        """Получить список рецензий фильма с гибкой сортировкой."""
        user_id = payload.get("user_id")

        log_info = (
            f"Получение списка закладок на фильмы. user_id={user_id}"
        )
        logger.info(log_info)

        #  todo


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
