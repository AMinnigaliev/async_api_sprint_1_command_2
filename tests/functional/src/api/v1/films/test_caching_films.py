import aiohttp
import pytest
import time

from logger import logger
from settings import config


@pytest.mark.skipif(config.skip_test == "true", reason="Temporary")  # TODO:
@pytest.mark.asyncio
async def test_search_with_cache(load_bulk_data_to_es) -> None:
    """
    Тест проверяет, что при повторном запросе по одному и тому же поисковому запросу
    результат возвращается из кеша Redis.

    @type load_bulk_data_to_es:
    @param load_bulk_data_to_es:
    @rtype None:
    """
    query_data = {"search": "The Star", "page_size": 5, "page_number": 1}

    logger.info("Массовая загрузка данных в Elasticsearch")
    es_data = await load_bulk_data_to_es
    logger.info(f"Успешно загружено {len(es_data)} фильмов в индекс {config.es_index}.")

    # Создаем HTTP-сессию
    async with aiohttp.ClientSession() as session:
        # Первый запрос (предварительное заполнение кэша)
        start = time.monotonic()
        async with session.get(f"{config.service_url}/api/v1/search/films_by_title", params=query_data) as response:
            body1 = await response.json()
            first_duration = time.monotonic() - start
            assert response.status == 200, f"Первый запрос: ожидался статус 200, получен: {response.status}"

        # Второй запрос (ожидается, что ответ будет возвращён из кеша и время будет меньше)
        start = time.monotonic()
        async with session.get(f"{config.service_url}/api/v1/search/films_by_title", params=query_data) as response:
            body2 = await response.json()
            second_duration = time.monotonic() - start
            assert response.status == 200, f"Второй запрос: ожидался статус 200, получен: {response.status}"

    # Сравниваем длительности запросов; второй запрос должен выполняться быстрее, если результат берётся из кеша.
    logger.info(f"Время первого запроса: {first_duration:.4f} сек, второго запроса: {second_duration:.4f} сек")
    assert second_duration < first_duration, (
        "Время выполнения второго запроса не меньше, чем первого. Проверьте работу кеша Redis."
    )
    # Можно также проверить, что ответы идентичны
    assert body1 == body2, "Ответы первого и второго запроса должны совпадать"
