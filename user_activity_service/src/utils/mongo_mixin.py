import logging.config
from typing import Any

from fastapi import HTTPException, status
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class MongoMixin:
    """Mixin для операций с MongoDB."""

    @staticmethod
    async def _get_count_documents(collection, filters: dict[str, Any], error_msg: str = None):
        """
        Получение кол-ва документов в коллекции в Mongo.

        @type filters:
        @param filters:
        @type collection:
        @param collection:
        @type error_msg:
        @param error_msg:
        @rtype:
        """
        try:
            return await collection.count_documents(filters)

        except PyMongoError as ex:
            logger.error(f"Error update in mongo: {ex}")

            default_error_msg = f"Error get count documents (collection: {collection}, filters: {filters} in Mongo)"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg if error_msg else default_error_msg,
            )

    @staticmethod
    async def _get_collection_docs_with_pagination(
        collection,
        filters: dict[str, Any],
        skip: int,
        sort_field: str,
        per_page: int,
        sort_direction: int = ASCENDING,
        error_msg: str = None
    ):
        """
        Получение документов в коллекции в Mongo с пагинацией.

        @type filters:
        @param filters:
        @type collection:
        @param collection:
        @type skip:
        @param skip:
        @type sort_field:
        @param sort_field:
        @type per_page:
        @param per_page:
        @type error_msg:
        @param error_msg:
        @rtype:
        """
        try:
            return await (
                collection.find(filters)
                .sort(sort_field, sort_direction)
                .skip(skip)
                .limit(per_page)
            )

        except PyMongoError as ex:
            logger.error(f"Error get docs with pagination in mongo: {ex}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg if error_msg else f"Error get docs with pagination by filters {filters} in Mongo",
            )

    @staticmethod
    async def _insert_in_mongo(doc_: dict[str, Any], collection, error_msg: str = None, log_msg: str = None) -> str:
        """
        Добавление документа в Mongo.

        @type doc_:
        @param doc_:
        @type collection:
        @param collection:
        @type error_msg:
        @param error_msg:
        @type log_msg:
        @param log_msg:
        @rtype:
        """
        try:
            result = await collection.insert_one(**doc_)

            if log_msg:
                logger.info(log_msg)

            return str(result.inserted_id)

        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg if error_msg else f"Error insert data in Mongo (collection: {collection}, {doc_})",
            )

    @staticmethod
    async def _get_one_from_mongo(filters: dict[str, Any], collection, error_msg: str = None):
        """
        Получение документа в Mongo.

        @type filters:
        @param filters:
        @type collection:
        @param collection:
        @type error_msg:
        @param error_msg:
        @rtype:
        """
        if doc_ := await collection.find_one(filters):
            return doc_

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg if error_msg else f"Not found data in collection {collection} by filters {filters}",
            )

    @staticmethod
    async def _update_in_mongo(
        filters: dict[str, Any],
        update_data: dict[str, Any],
        collection,
        error_msg: str = None,
        log_msg: str = None,
    ) -> None:
        """
        Обновление документа в Mongo.

        @type filters:
        @param filters:
        @type update_data:
        @param update_data:
        @type collection:
        @param collection:
        @type error_msg:
        @param error_msg:
        @type log_msg:
        @param log_msg:
        @rtype:
        """
        try:
            await collection.update_one(filters, {"$set": update_data})

            if log_msg:
                logger.info(log_msg)

        except PyMongoError as ex:
            logger.error(f"Error update in mongo: {ex}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg if error_msg else f"Error update data {update_data} by filters {filters} in Mongo",
            )

    @staticmethod
    async def _delete_in_mongo(
        filters: dict[str, Any],
        collection,
        error_msg: str = None,
        log_msg: str = None,
    ) -> None:
        """
        Удаление документа в Mongo.

        @type filters:
        @param filters:
        @type collection:
        @param collection:
        @type error_msg:
        @param error_msg:
        @type log_msg:
        @param log_msg:
        @rtype:
        """
        try:
            await collection.delete_one(filters)

            if log_msg:
                logger.info(log_msg)

        except PyMongoError as ex:
            logger.error(f"Error delete in mongo: {ex}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg if error_msg else f"Error delete data by filters {filters} in Mongo",
            )
