import asyncio
import logging
from typing import Any, Type

import orjson
from elasticsearch import NotFoundError
from pydantic import BaseModel, ValidationError

from src.core.exceptions import (CacheServiceError, CheckCacheError,
                                 CheckElasticError, CreateObjectError,
                                 CreateObjectsError, ElasticParsingError,
                                 ElasticServiceError, JsonLoadsError,
                                 ModelDumpError, ModelDumpJsonError)
from src.utils.cache_service import CacheService
from src.utils.elastic_service import ElasticService

logger = logging.getLogger(__name__)


class BaseService:
    """
    Базовый сервис.

    Осуществляет взаимодействие с Redis (для кеширования)
    и Elasticsearch (для полнотекстового поиска).
    """

    def __init__(self, redis_client: CacheService, es_client: ElasticService):
        self.redis_client = redis_client
        self.es_client = es_client

    @staticmethod
    def _model_dump(
        obj: BaseModel,
        exclude: set[str] | dict | None = None,
        log_info: str = "",
    ) -> dict:
        """
        Вспомогательный метод для генерации словаря из объекта модели Pydantic.
        """
        try:
            return obj.model_dump(
                mode='json', exclude=exclude
            )

        except (AttributeError, TypeError, ValueError, KeyError) as e:
            logger.error(
                "Ошибка при сериализации объекта модели %s с ID %s в словарь: "
                "%s. %s",
                obj.id, obj.__class__.__name__, e, log_info
            )
            raise ModelDumpError(e)

    @staticmethod
    def _create_object_from_dict(
        model: Type[BaseModel], data: dict, log_info: str = ""
    ) -> BaseModel:
        """
        Вспомогательный метод для создания объекта модели Pydantic из словаря.
        """
        try:
            return model(**data)

        except ValidationError as e:
            logger.warning(
                "Ошибка при валидации из словаря в модель %s: %s. "
                "Данные для валидации: %s. %s",
                model.__name__, e, data, log_info
            )
            raise CreateObjectError(e.json())

    @staticmethod
    def _get_record_from_source(data: dict, log_info: str = "") -> dict:
        """
        Вспомогательный метод для извлечения данных по записи из Elasticsearch.
        """
        try:
            record = data["_source"]
            if isinstance(record, dict):
                return record
            raise TypeError(
                "Ожидался dict, но получен %s. %s",
                type(record).__name__, log_info
            )

        except (KeyError, TypeError) as e:
            logger.error(
                "Ошибка в структуре данных из Elasticsearch: %s"
                "Переданные данные для получения значения по ключа "
                "'_source': %s. %s",
                e, data, log_info
            )
            raise ElasticParsingError(e)

    @staticmethod
    def _get_records_from_hits(data: dict, log_info: str = "") -> list[dict]:
        """
        Вспомогательный метод для извлечения списка записей из Elasticsearch.
        """
        try:
            return data["hits"]["hits"]

        except (KeyError, TypeError) as e:
            logger.error(
                "Ошибка некорректного ответа от Elasticsearch: %s. %s",
                e, log_info
            )
            raise ElasticParsingError(e)

    @staticmethod
    def _get_data_from_json(json: bytes | None, log_info: str = "") -> Any:
        """Вспомогательный метод для десериализации JSON в объекты Python."""
        try:
            return orjson.loads(json)

        except orjson.JSONDecodeError as e:
            logger.warning(
                "Ошибка при попытки декодировать json в объект Python. "
                "json: %s. %s",
                json, log_info
            )
            raise JsonLoadsError(e)

    def _create_objects(
        self,
        model: Type[BaseModel],
        data: list[dict],
        is_it_cache: bool = False,
        log_info: str = "",
    ) -> list[BaseModel]:
        """
        Вспомогательный метод для создания списка с объектами модели Pydantic.
        """
        valid_objects = []

        for cell in data:
            try:
                record = self._get_record_from_source(cell)

            except ElasticParsingError:
                pass

            else:
                try:
                    model_obj = self._create_object_from_dict(model, record)

                except CreateObjectError as e:
                    if is_it_cache:
                        raise CreateObjectError(e)
                    pass

                else:
                    valid_objects.append(model_obj)

        if not valid_objects:
            if data:
                message = (
                    f"Не удалось создать ни одного объекта модели "
                    f"{model.__name__} из переданных данных: {data}. "
                    f"{log_info}"
                )
                logger.error(message)

                raise CreateObjectsError(message)

        return valid_objects

    def _create_json_from_objects(
        self, data: list[BaseModel], log_info: str = ""
    ) -> bytes:
        """
        Вспомогательный метод для создания json из списка объектов Pydantic.
        """
        valid_data = []
        try:
            for model_obj in data:
                try:
                    model_data = self._model_dump(model_obj)

                except ModelDumpError as e:
                    raise ModelDumpJsonError(e)

                else:
                    valid_data.append({"_source": model_data})

        except TypeError as e:
            logger.error(
                "Кеширование не выполняется по причине ошибки при обращении к "
                "Elasticsearch. %s",
                log_info
            )
            raise ModelDumpJsonError(e)

        else:
            try:
                return orjson.dumps(data)

            except orjson.JSONEncodeError as e:
                logger.error(
                    "Ошибка сериализации списка записей в виде словарей в json: "
                    "%s. Входные данные: %s. %s",
                    e, data, log_info
                )
                raise ModelDumpJsonError(e)

    async def _get_from_cache(
            self, model: Type[BaseModel], cache_key: str, log_info: str = ""
    ):
        try:
            cache_json = await self.redis_client.get(cache_key, log_info)
            cache_data = self._get_data_from_json(cache_json, log_info)
            result = self._create_objects(model, cache_data, True, log_info)

        except (
            CacheServiceError, JsonLoadsError, CreateObjectError,
            CreateObjectsError
        ) as e:
            raise CheckCacheError(e)

        else:
            logger.info("Данные из кеша прошли валидацию. %s", log_info)

            return result

    async def _get_from_elastic(
        self,
        model: Type[BaseModel],
        index: str,
        body: dict,
        log_info: str = "",
    ) -> list[BaseModel] | None:
        """Вспомогательный метод для поиска записей в Elasticsearch."""
        try:
            response = await self.es_client.search(
                index, body, log_info)
            records_data = self._get_records_from_hits(response, log_info)
            records_obj = self._create_objects(
                model, records_data, False, log_info
            )

        except (
            ElasticServiceError, ElasticParsingError, CreateObjectsError
        ) as e:
            raise CheckElasticError(e)

        except NotFoundError:
            logger.info(
                "Запись с ID %s не найдена в Elasticsearch. %s", id, log_info
            )
            return []

        else:
            logger.info(
                "Из Elasticsearch получено записей в количестве: %d шт. %s",
                len(records_obj), log_info
            )
            return records_obj

    async def _put_to_cache(
        self, cache_key: str, data: list[BaseModel] | str, log_info: str = ""
    ) -> None:
        """Вспомогательные метод для кеширования записей."""
        try:
            json_represent = self._create_json_from_objects(
                data, log_info
            )
            await self.redis_client.set(cache_key, json_represent, log_info)

        except (CacheServiceError, ModelDumpJsonError):
            pass

    async def _base_get_no_cache(
            self,
            model: Type[BaseModel],
            index: str,
            body: dict,
            log_info: str,
    ) -> list[BaseModel] | None:
        """
        Вспомогательный базовый метод для получения записей без использования
        кеша.
        """
        # Проверяем наличие результата в Elasticsearch
        try:
            obj = await self._get_from_elastic(
                model, index, body, log_info
            )
        except CheckElasticError:
            return None

        else:
            return obj

    async def _base_get_with_cache(
            self,
            model: Type[BaseModel],
            index: str,
            body: dict,
            cache_key: str,
            log_info: str,
    ) -> list[BaseModel] | None:
        """
        Вспомогательный базовый метод для получения записей с использованием
        кеша.
        """
        # Проверяем наличие результата в кеше (Redis)
        try:
            cache = await self._get_from_cache(
                model, cache_key, log_info
            )
            return cache

        except CheckCacheError:
            pass

        # Проверяем наличие результата в Elasticsearch
        result = await self._base_get_no_cache(model, index, body, log_info)

        # Кешируем асинхронно фильм в Redis
        asyncio.create_task(self._put_to_cache(cache_key, result, log_info))

        return result
