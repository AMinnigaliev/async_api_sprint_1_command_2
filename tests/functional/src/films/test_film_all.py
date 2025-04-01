import aiohttp
import pytest

from settings import config


@pytest.mark.asyncio
async def test_get_all_films(load_bulk_data_to_es) -> None:
    """
    Проверяем, что API возвращает список всех фильмов.

    @type load_bulk_data_to_es:
    @param load_bulk_data_to_es:
    @rtype None:
    """
    await load_bulk_data_to_es  # Загружаем тестовые фильмы

    async with aiohttp.ClientSession() as session:
        url = f"{config.service_url}/api/v1/films/"

        async with session.get(url) as response:
            assert response.status == 200, f"Ожидался 200, но получен {response.status}"
            assert isinstance(await response.json(), list), "Ответ должен быть списком"
            assert len(await response.json()) > 0, "Список фильмов не должен быть пустым"
