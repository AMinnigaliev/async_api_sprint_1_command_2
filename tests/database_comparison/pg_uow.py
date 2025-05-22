import os
import time

from dotenv import load_dotenv
from psycopg import connection as pg_connection_, sql

from tests.database_comparison.logger import logger

load_dotenv()


class PGUOW:

    configs = {
        "dbname": os.getenv("POSTGRES_DB", "test_db"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }

    def __init__(self, connection_: pg_connection_) -> None:
        self._connection = connection_

    def init_pg(self, table_name: str, columns: list[str, str | dict[str, str]]) -> None:
        with self._connection.cursor() as pg_cursor:
            query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(
                    [
                        sql.SQL(col) if not isinstance(col, dict) or 'references' not in col
                        else sql.SQL("FOREIGN KEY ({}) REFERENCES {} ({})").format(
                            sql.Identifier(col['column']),
                            sql.Identifier(col['references']['table']),
                            sql.Identifier(col['references']['column'])
                        ) for col in columns if
                        isinstance(col, str)
                        or (isinstance(col, dict) and col.get("shard_key") is None and col.get("indexes") is None)
                    ]
                )
            )
            pg_cursor.execute(query)

            logger.debug(f"PG: таблица {table_name} создана")

    def drop_tables(self, table_name: str) -> None:
        with self._connection.cursor() as pg_cursor:
            pg_cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")

        logger.debug(f"PG: таблица '{table_name}' удалена")

    def insert_data(self, table_name: str, insert_data: list[dict]):
        with self._connection.cursor() as pg_cursor:
            pg_data = list()

            for data_ in insert_data:
                pg_data.append([data_[key] for key in data_.keys()])

            if pg_data:
                columns = list(insert_data[0].keys())
                columns_str = ", ".join(columns)

                start_ = time.perf_counter()
                values_count = ",".join(["%s" for _ in range(len(columns))])
                pg_cursor.executemany(
                    f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_count})",
                    pg_data
                )

                end_ = time.perf_counter()
                insert_time = end_ - start_

        self._connection.commit()
        logger.debug(
            f"PG: в таблицу '{table_name}' добавлены данные "
            f"(кол-во: {len(insert_data)}, время выполнения: {insert_time:.5f} сек.)"
        )

        return insert_time

    def select_data(self, table_name: str, filters_: dict[str, dict[str, str]]) -> tuple:
        with self._connection.cursor() as pg_cursor:
            start_ = time.perf_counter()
            filter_and_str = (
                " AND ".join(
                    f"{table_name}.{column} {conditions['operator']} {conditions['value']}"
                    for column, conditions in filters_.items()
                )
            )

            pg_cursor.execute(f"SELECT * FROM {table_name} WHERE {filter_and_str};")
            user_rating_films = pg_cursor.fetchall()

            end_ = time.perf_counter()
            select_time = end_ - start_

            logger.debug(
                f"PG: из таблицы '{table_name}' произведен select по фильтрам: {filter_and_str} "
                f"(кол-во: {len(user_rating_films)}, время выполнения: {select_time:.5f} сек.)"
            )

            return list(user_rating_films), select_time
