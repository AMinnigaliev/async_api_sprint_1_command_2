import aiohttp
import pytest

from logger import logger
from settings import config


@pytest.mark.asyncio
async def test_get_film_by_uuid(load_bulk_data_to_es) -> None:
    """
    Проверяем, что можно получить фильм по UUID.

    @type load_bulk_data_to_es:
    @param load_bulk_data_to_es:
    @rtype None:
    """
    test_film = (await load_bulk_data_to_es)[0]  # Загружаем тестовые данные
    film_uuid = test_film["uuid"]

    async with aiohttp.ClientSession() as session:
        url = f"{config.service_url}/api/v1/films/{film_uuid}"

        async with session.get(url) as response:
            assert response.status == 200, f"Ожидался 200, но получен {response.status}"

            data = await response.json()
            logger.debug(f"Ответ сервера: {data}")  # <-- Вывод JSON для проверки

            # Исправленный тест: Проверяем "uuid" вместо "id"
            assert "uuid" in data, "Ответ не содержит uuid"
            assert data["uuid"] == film_uuid, f"UUID не верный: ожидался {film_uuid}, получен {data['uuid']}"
