import uuid
import aiohttp
import pytest

from logger import logger
from settings import config


@pytest.mark.skipif(config.skip_test == "true", reason="Temporary")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query_data",
    [{"search": "", "page_size": 5, "page_number": 1}],  # Параметры поиска
)
async def test_no_search_parameter(es_client, load_bulk_data_to_es, query_data: dict) -> None:
    """
    Тест проверяет поиск фильмов через Elasticsearch и API.

    @type es_client:
    @param es_client:
    @type load_bulk_data_to_es:
    @param load_bulk_data_to_es:
    @type query_data: dict
    @param query_data:
    @rtype None:
    """
    logger.info("Начало теста: test_search")

    try:
        # Массовая загрузка данных
        logger.info("Массовая загрузка данных в Elasticsearch")
        es_data = await load_bulk_data_to_es
        logger.info(f"Успешно загружено {len(es_data)} фильмов в индекс {config.es_index}.")

        # Создаем HTTP-сессию
        async with aiohttp.ClientSession() as session:
            url = f"{config.service_url}/api/v1/search/films_by_title"
            response = await session.get(url, params=query_data)
            body = await response.json()
            status = response.status

        # Проверяем результат
        logger.info(f"Получен ответ от API. Статус: {status}, тело ответа: {body}")
        assert status == 500, f"Ожидался статус 500, получен: {status}"
        assert len(body) == 1, f"Ожидалось 1 записей, получено: {len(body)}"
        logger.info("Тест успешно завершен.")

    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"Ошибка при выполнении теста (ID: {error_id}): {e}")
        raise
