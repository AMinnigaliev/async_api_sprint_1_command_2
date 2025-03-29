import time
import pytest
import aiohttp

from logger import logger
from settings import config


@pytest.mark.skipif(config.skip_test == "true", reason="Temporary")
@pytest.mark.asyncio
async def test_film_caching(load_bulk_data_to_es) -> None:
    """
    Проверяем, что фильм кэшируется в Redis:
    первый запрос медленный (идёт в ES), второй — быстрый (из кэша).

    @type load_bulk_data_to_es:
    @param load_bulk_data_to_es:
    @rtype None:
    """
    logger.info("Массовая загрузка данных в Elasticsearch")
    es_data = await load_bulk_data_to_es
    assert es_data, "Ошибка загрузки тестовых данных в ES"

    film_uuid = es_data[0]["uuid"]  # Берём UUID первого фильма
    url = f"{config.service_url}/api/v1/films/{film_uuid}"

    async with aiohttp.ClientSession() as session:
        # Первый запрос (должен идти в ES)
        start = time.monotonic()
        async with session.get(url) as response:
            body1 = await response.json()
            first_duration = time.monotonic() - start
            assert response.status == 200, f"Первый запрос: ожидался 200, получен {response.status}"

        # Второй запрос (должен идти в Redis)
        start = time.monotonic()
        async with session.get(url) as response:
            body2 = await response.json()
            second_duration = time.monotonic() - start
            assert response.status == 200, f"Второй запрос: ожидался 200, получен {response.status}"

    # Проверка времени выполнения
    logger.info(f"Время первого запроса: {first_duration:.4f} сек, второго: {second_duration:.4f} сек")
    assert second_duration < first_duration, "Кэш не работает, второй запрос не быстрее первого"

    # Проверка идентичности ответа
    assert body1 == body2, "Ответы должны совпадать"
