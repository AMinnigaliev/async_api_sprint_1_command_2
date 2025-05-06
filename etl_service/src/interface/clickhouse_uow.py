import socket
from typing import TypeVar

from sqlalchemy.exc import SQLAlchemyError

from utils import backoff_by_connection
from db.clickhouse_session import clickhouse_scoped_

__all__ = ["ClickhouseUOW_T", "ClickhouseUOWContextManager", "clickhouse_uow_"]

ClickhouseUOW_T = TypeVar("ClickhouseUOW_T", bound="ClickhouseUOWContextManager")


class ClickhouseUOWContextManager:
    """Контекстный менеджер по работе с session Clickhouse."""

    ERROR_EXC_TYPES = [
        SQLAlchemyError,
    ]

    def __init__(self, scoped_session_) -> None:
        self._scoped_session = scoped_session_

    def __enter__(self):
        return self._scoped_session.session

    @backoff_by_connection(exceptions=(ConnectionRefusedError, socket.gaierror))
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type in self.ERROR_EXC_TYPES:
            self._scoped_session.session.rollback()

        self._scoped_session.session.close()


clickhouse_uow_ = ClickhouseUOWContextManager(scoped_session_=clickhouse_scoped_)
