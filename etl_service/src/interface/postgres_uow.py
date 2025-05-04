import socket
from typing import Optional, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession as AlchemyAsyncSession

from db.pg_session import AsyncScopedSession, async_session, scoped_session
from utils import backoff_by_connection

__all__ = ["DataBaseUOW_T", "DataBaseUOWContextManager", "db_uow_"]

DataBaseUOW_T = TypeVar("DataBaseUOW_T", bound="DataBaseUOWContextManager")


class DataBaseUOWContextManager:
    """Контекстный менеджер по работе с session DB."""

    ERROR_EXC_TYPES = [
        SQLAlchemyError,
    ]

    def __init__(self, async_scoped_session_: AsyncScopedSession) -> None:
        self._async_scoped_session = async_scoped_session_
        self._async_session: Optional[AlchemyAsyncSession] = None

    async def __aenter__(self) -> async_session:
        self._async_session = (
            await self._async_scoped_session.get_async_scoped_session()
        )
        return self._async_session

    @backoff_by_connection(exceptions=(ConnectionRefusedError, socket.gaierror))
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type in self.ERROR_EXC_TYPES:
            await self._async_session.rollback()

        await self._async_session.close()


db_uow_ = DataBaseUOWContextManager(async_scoped_session_=scoped_session)
