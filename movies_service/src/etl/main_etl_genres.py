import asyncio
# Настройка логирования
import logging.config

from elasticsearch import AsyncElasticsearch

from src.core.config import settings  # Импортируем настройки
from src.core.logger import LOGGING
from src.etl.etl_genres import ETLService

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def main():
    """
    Основная функция для запуска ETL-процесса.
    """
    try:
        # Создание асинхронного клиента Elasticsearch
        logger.info("Инициализация клиента Elasticsearch...")
        es_client = AsyncElasticsearch(
            hosts=[
                f"{settings.elastic_scheme}://{settings.elastic_host}:"
                f"{settings.elastic_port}"
            ],
            basic_auth=(settings.elastic_name, settings.elastic_password),
            request_timeout=30,
        )

        # Проверка соединения с Elasticsearch
        if not await es_client.ping():
            raise ConnectionError("Не удалось подключиться к Elasticsearch.")

        # Инициализация ETL-сервиса
        etl_service = ETLService(elastic=es_client)

        # Запуск ETL-процесса
        logger.info("Запуск ETL-процесса для жанров...")
        films_index = "films"  # Индекс фильмов
        genres_index = "genres"  # Индекс жанров

        await etl_service.run_etl(
            films_index=films_index, genres_index=genres_index
        )

    except ConnectionError as e:
        logger.error(f"Ошибка подключения к Elasticsearch: {e}")
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}", exc_info=True)
    finally:
        # Корректное закрытие соединения с Elasticsearch
        logger.info("Закрытие соединения с Elasticsearch...")
        if "es_client" in locals() and es_client is not None:
            await es_client.close()
        logger.info("Соединение успешно закрыто.")

if __name__ == "__main__":
    # Запуск асинхронного ETL-процесса
    asyncio.run(main())
