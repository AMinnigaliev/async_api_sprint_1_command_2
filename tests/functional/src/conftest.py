import uuid

import pytest
from elasticsearch.helpers import async_bulk

from settings import config


@pytest.fixture
def generate_film_data():
    """
    Фикстура для генерации данных фильма. Может создавать один или несколько фильмов.

    @rtype: None
    @return:
    """
    def _generate_film_data(count: int = 1) -> list[dict]:
        """
        Генерирует указанное количество фильмов.

        @type count: int
        @param count: Количество фильмов.

        @rtype films: list[dict]
        @return films: Список данных фильмов (если count > 1) или один фильм.
        """
        films = []
        for _ in range(count):
            film = {
                'uuid': str(uuid.uuid4()),  # Уникальный идентификатор фильма
                'genre': [
                    {'uuid': str(uuid.uuid4()), 'name': 'Action'},
                    {'uuid': str(uuid.uuid4()), 'name': 'Sci-Fi'}
                ],
                'title': 'The Star',
                'description': 'New World',
                'actors': [
                    {'uuid': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Ann'},
                    {'uuid': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'full_name': 'Bob'}
                ],
                'writers': [
                    {'uuid': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Ben'},
                    {'uuid': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'Howard'}
                ],
                'directors': [
                    {'uuid': str(uuid.uuid4()), 'full_name': 'Stan'}
                ],
                'imdb_rating': 8.5
            }
            films.append(film)
        return films if count > 1 else films[0]

    return _generate_film_data


@pytest.fixture
async def load_bulk_data_to_es(es_client, generate_film_data) -> list[dict]:
    """
    Асинхронная фикстура для массовой загрузки данных фильмов в Elasticsearch.

    @type es_client:
    @param es_client: Асинхронный клиент Elasticsearch.
    @type generate_film_data:
    @param generate_film_data: Фикстура для генерации данных фильмов.

    @rtype es_data: list[dict]
    @return es_data: Загруженные данные фильмов.
    """
    index_name = config.elastic_index
    count = 5  # Можно задать другое значение в тесте, если нужно

    # Генерируем данные фильмов
    es_data = generate_film_data(count=count)

    # Удаляем индекс, если он существует
    if await es_client.indices.exists(index=index_name):
        await es_client.indices.delete(index=index_name)

    # Создаем индекс с маппингом
    await es_client.indices.create(index=index_name, body=config.elastic_index_mapping)

    # Формируем bulk-запрос
    bulk_query = [
        {
            '_index': index_name,
            '_id': film['uuid'],
            '_source': film
        }
        for film in es_data
    ]

    # Выполняем bulk-запрос
    success, failed = await async_bulk(
        client=es_client,
        actions=bulk_query,
        refresh='wait_for'
    )
    if failed:
        raise Exception(f"Не удалось загрузить {len(failed)} записей: {failed}")

    return es_data


@pytest.fixture
def generate_person_data():
    """
    Фикстура для генерации данных персоны. Может создавать одну или несколько персон.

    @rtype:
    @return: Функция-генератор данных персоны.
    """
    def _generate_person_data(count=1):
        """
        Генерирует указанное количество фильмов.

        @type count: int
        @param count: Количество персон.

        @rtype persons: list[dict]
        @return persons: Список данных персон (если count > 1) или одна персона.
        """
        persons = []
        for _ in range(count):
            person = {
                "uuid": str(uuid.uuid4()),
                "full_name": "John Doe",
                "films": [
                    {
                        "uuid": str(uuid.uuid4()),
                        "roles": ["actor", "director"]
                    },
                    {
                        "uuid": str(uuid.uuid4()),
                        "roles": ["writer"]
                    }
                ]
            }
            persons.append(person)
        return persons if count > 1 else persons[0]

    return _generate_person_data


@pytest.fixture
async def load_bulk_data_to_persons_es(es_client, generate_person_data):
    """
    Асинхронная фикстура для массовой загрузки данных персон в Elasticsearch.

    @type es_client:
    @param es_client: Асинхронный клиент Elasticsearch.
    @type generate_person_data:
    @param generate_person_data: Фикстура для генерации данных персон.

    @rtype es_data: list[dict]
    @return es_data: Загруженные данные персон.
    """
    index_name = 'persons'
    count = 5  # Можно задать другое значение в тесте, если нужно

    # Генерируем данные фильмов
    es_data = generate_person_data(count=count)

    # Удаляем индекс, если он существует
    if await es_client.indices.exists(index=index_name):
        await es_client.indices.delete(index=index_name)

    # Создаем индекс с маппингом
    await es_client.indices.create(index=index_name, body=config.elastic_index_mapping)

    # Формируем bulk-запрос
    bulk_query = [
        {
            '_index': index_name,
            '_id': person['uuid'],
            '_source': person
        }
        for person in es_data
    ]

    # Выполняем bulk-запрос
    success, failed = await async_bulk(
        client=es_client,
        actions=bulk_query,
        refresh='wait_for'
    )
    if failed:
        raise Exception(f"Не удалось загрузить {len(failed)} записей: {failed}")

    return es_data
