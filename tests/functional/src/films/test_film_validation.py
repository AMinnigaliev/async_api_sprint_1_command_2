import aiohttp
import pytest

from logger import logger
from settings import config


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_uuid",
    ["abc", "123456789", "ffffffff-ffff-ffff", "123e4567-e89b-12d3-a456-4266141740000"],
)
async def test_get_film_invalid_uuid(invalid_uuid):
    """
    Проверяем, что API возвращает 422, если передан некорректный UUID.

    @type load_bulk_data_to_es:
    @param load_bulk_data_to_es:
    @rtype None:
    """
    async with aiohttp.ClientSession() as session:
        url = f"{config.service_url}/api/v1/films/{invalid_uuid}"

        async with session.get(url) as response:
            logger.debug(f"Статус-код ответа: {response.status}")

            assert response.status == 422, f"Ожидался 422, но получен {response.status}"
