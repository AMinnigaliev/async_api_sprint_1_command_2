from contextlib import contextmanager

from infi.clickhouse_orm import Database

from core import config
from core.logger import logger
from utils.abstract import SingletonMeta


class ClickhouseSession(metaclass=SingletonMeta):
    ERROR_EXC_TYPES = [Exception,]

    def __init__(self):
        self._db = Database(
            db_name=config.clickhouse_db,
            db_url=(
                f"http://{config.clickhouse_host}:"
                f"{config.clickhouse_http_port}"
            ),
            username=config.clickhouse_user,
            password=config.clickhouse_password,
            readonly=False,
        )

    @property
    def session(self) -> Database:
        return self._db

    @contextmanager
    def context_session(self):
        try:
            yield self._db

        except tuple(self.ERROR_EXC_TYPES) as ex:
            logger.error(f"ClickHouse ORM error: {ex}")
            raise

        finally:
            pass


clickhouse_session = ClickhouseSession()
