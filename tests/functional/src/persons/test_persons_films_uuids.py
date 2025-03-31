import uuid
import aiohttp
import pytest

from logger import logger
from settings import config


@pytest.mark.skipif(config.skip_test == "true", reason="Temporary")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query_data",
    [{"search": "John Doe", "page_size": 5, "page_number": 1}],  # Параметры поиска по полному имени персоны
)
async def test_persons_films_uuids(es_client, load_bulk_data_to_persons_es, query_data: dict) -> None:
    """
    Тест проверяет поиск персон по полному имени через Elasticsearch и API.

    @type es_client:
    @param es_client:
    @type load_bulk_data_to_persons_es:
    @param load_bulk_data_to_persons_es:
    @type query_data: dict
    @param query_data:
    @rtype None:
    """
    logger.info("Начало теста: test_persons_films_uuids")

    try:
        # Массовая загрузка данных в индекс Elasticsearch
        logger.info("Массовая загрузка данных в Elasticsearch")
        es_data = await load_bulk_data_to_persons_es
        logger.info(f"Успешно загружено {len(es_data)} персон в индекс {config.es_persons_index_mapping}.")

        # Создаем HTTP-сессию для запроса к API
        async with aiohttp.ClientSession() as session:
            url = f"{config.service_url}/api/v1/persons/persons_films_uuids"
            response = await session.get(url, params=query_data)
            body = await response.json()
            status = response.status

        # Логирование и проверка результата
        logger.info(f"Получен ответ от API. Статус: {status}, тело ответа: {body}")
        assert status == 200, f"Ожидался статус 200, получен: {status}"
        assert len(body) == 10, f"Ожидалось 10 записей, получено: {len(body)}"
        logger.info("Тест успешно завершен.")

    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"Ошибка при выполнении теста (ID: {error_id}): {e}")
        raise
