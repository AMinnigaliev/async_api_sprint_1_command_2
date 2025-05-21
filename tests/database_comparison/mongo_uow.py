import os
import time

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.synchronous.client_session import ClientSession as MongoSession

from tests.database_comparison.logger import logger

load_dotenv()


class MongoUOW:

    client_url = {
        "with_shard": (
            f"mongodb://{os.getenv('MONGO_HOST', 'localhost')}:{os.getenv('MONGO_SHARD_PORT', '27019')}"
            f"/?authSource=admin"
        ),
        "without_shard": f"mongodb://{os.getenv('MONGO_HOST', 'localhost')}:{os.getenv('MONGO_PORT', '27017')}/"
    }

    def __init__(self, client: MongoClient, session: MongoSession):
        self._client = client
        self._db = client[os.getenv("MONGO_DB", "test_db")]
        self._session = session

    def init_mongo(self, collection_name: str, shard_key: str = None, indexes: list[str] = None) -> None:
        if collection_name not in self._db.list_collection_names():
            self._db.create_collection(
                name=collection_name,
                session=self._session,
            )
            logger.debug(f"Mongo: коллекций {collection_name} создана")

            collection = self._db[collection_name]
            if indexes and bool(int(os.getenv("MONGO_WITH_INDEX", 1))):
                for index in indexes:
                    collection.create_index([(index, ASCENDING)])
                    logger.debug(f"Mongo: для коллекции '{collection_name}' создан индекс по полю '{index}'(ASCENDING)")

            if shard_key and bool(int(os.getenv("MONGO_WITH_SHARD", 1))):
                admin_db = self._client.admin
                admin_db.command("enableSharding", collection_name)
                admin_db.command(
                    {
                        "shardCollection": f"{os.getenv('MONGO_DB', 'test_db')}.{collection_name}",
                        "key": {shard_key: 'hashed'}  # Хэш-распределение
                    }
                )
                logger.debug(f"Mongo: для коллекции '{collection_name}' добавлен ключ шардирования '{shard_key}'")

        else:
            logger.debug(f"Mongo: коллекция '{collection_name}' уже создана.")

    def drop_collections(self, collection_name: str):
        if collection_name in self._db.list_collection_names():
            self._db[collection_name].drop()

        logger.debug(f"Mongo: коллекция '{collection_name}' удалена")

    def insert_data(self, collection_name: str, insert_data: list[dict]):
        collection = self._db[collection_name]

        start_ = time.perf_counter()
        collection.insert_many(insert_data, session=self._session, ordered=False, bypass_document_validation=True)

        end_ = time.perf_counter()
        insert_time = end_ - start_

        logger.debug(
            f"Mongo: в коллекцию '{collection_name}' добавлены данные "
            f"(кол-во: {len(insert_data)}, время выполнения: {insert_time:.5f} сек.)"
        )
        return insert_time

    def select_data(self, collection_name: str, filters_: dict[str, str | dict[str, str | int]]) -> tuple:
        collection = self._db[collection_name]

        start_ = time.perf_counter()
        user_rating_films = collection.find(filters_, session=self._session)
        user_rating_films_lst = list(user_rating_films)

        end_ = time.perf_counter()
        select_time = end_ - start_

        logger.debug(
            f"Mongo: из коллекции '{collection_name}' произведен select по фильтрам: {filters_}"
            f"(кол-во: {len(user_rating_films_lst)}, время выполнения: {select_time:.5f} сек.)"
        )

        return user_rating_films_lst, select_time
