import os
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient

import psycopg
from psycopg.rows import dict_row
from psycopg import ClientCursor as PGCursor

from tests.database_comparison.case_1 import user_like_rating_films_by_user
from tests.database_comparison.case_2 import user_like_rating_films_by_film
from tests.database_comparison.case_3 import user_film_markers_by_user
from tests.database_comparison.custom_enum import Models
from tests.database_comparison.gen_data import GenData
from tests.database_comparison.logger import logger
from tests.database_comparison.mongo_uow import MongoUOW
from tests.database_comparison.pg_uow import PGUOW

load_dotenv()


def create_db(pg_uow: PGUOW, mongo_uow: MongoUOW):
    for table_name, columns in Models.pg_create().items():
        pg_uow.init_pg(table_name=table_name, columns=columns)

        try:
            shard_key_m = next(iter([c["shard_key"] for c in columns if isinstance(c, dict) and c.get("shard_key")]))

        except StopIteration:
            shard_key_m = None

        try:
            indexes_m = next(iter([c["indexes"] for c in columns if isinstance(c, dict) and c.get("indexes")]))

        except StopIteration:
            indexes_m = None

        mongo_uow.init_mongo(collection_name=table_name, shard_key=shard_key_m, indexes=indexes_m)


def insert_data_in_db(pg_uow: PGUOW, mongo_uow: MongoUOW, gen_data: dict[str, Any]):
    for table_name in Models.pg_create().keys():
        insert_time_pg = pg_uow.insert_data(table_name=table_name, insert_data=gen_data.get(table_name))
        insert_time_mongo = mongo_uow.insert_data(collection_name=table_name, insert_data=gen_data.get(table_name))

        if insert_time_pg < insert_time_mongo:
            logger.info(
                f"{table_name}: "
                f"insert-запрос в PG({insert_time_pg}) выполнился быстрее, чем в Mongo({insert_time_mongo})"
            )

        elif insert_time_pg > insert_time_mongo:
            logger.info(
                f"{table_name}: "
                f"insert-запрос в Mongo({insert_time_mongo}) выполнился быстрее, чем в PG({insert_time_pg})"
            )

        elif insert_time_pg == insert_time_mongo:
            logger.info(
                f"{table_name}): insert-запрос в Mongo({insert_time_mongo}) и PG({insert_time_pg}) "
                "выполнился с одинаковой скоростью"
            )


def main():
    mongo_url_type = MongoUOW.client_url.get(
        "with_shard" if bool(int(os.getenv("MONGO_WITH_SHARD", 1))) else "without_shard"
    )
    mongo_client = MongoClient(mongo_url_type)

    with (
        mongo_client.start_session() as mongo_session,
        psycopg.connect(**PGUOW.configs, row_factory=dict_row, cursor_factory=PGCursor) as pg_connection
    ):
        pg_uow, mongo_uow = PGUOW(connection_=pg_connection), MongoUOW(client=mongo_client, session=mongo_session)

        count_entities = int(os.getenv("COUNT_ENTITIES", 250_000))
        gen_data = GenData(count_entities=count_entities if count_entities >= 10_000 else 10_000).run()

        try:
            create_db(pg_uow=pg_uow, mongo_uow=mongo_uow)
            insert_data_in_db(pg_uow=pg_uow, mongo_uow=mongo_uow, gen_data=gen_data)

            # Case_1: список понравившихся пользователю фильмов
            user_rating_film_data = next(iter(gen_data.get(Models.user_rating_films.name)))
            user_like_rating_films_by_user(pg_uow=pg_uow, mongo_uow=mongo_uow, user_id=user_rating_film_data["user_id"])

            # Case_2: количество лайков у определённого фильма
            user_like_rating_films_by_film(pg_uow=pg_uow, mongo_uow=mongo_uow, film_id=user_rating_film_data["film_id"])

            # Case_3: список закладок
            user_film_marker_data = next(iter(gen_data.get(Models.user_film_markers.name)))
            user_film_markers_by_user(pg_uow=pg_uow, mongo_uow=mongo_uow, user_id=user_film_marker_data["user_id"])

        finally:
            for table_name in Models.pg_create().keys():
                pg_uow.drop_tables(table_name=table_name)
                mongo_uow.drop_collections(collection_name=table_name)


if __name__ == "__main__":
    main()
