from asyncio import current_task
from typing import Any, Coroutine

from sqlalchemy.pool import NullPool
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError, InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession as AlchemyAsyncSession
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from core import config
from utils.abstract import SingletonMeta

__all__ = [
    "async_contextmanager_session",
    "async_session",
    "AsyncScopedSession",
    "scoped_session",
]


class BaseAsyncSession(metaclass=SingletonMeta):
    ERROR_EXC_TYPES = [
        SQLAlchemyError,
        InterfaceError,
    ]

    def __init__(self, async_engine) -> None:
        self._async_engine = async_engine
        self._async_session_factory = async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
        )


class AsyncScopedSession(BaseAsyncSession):
    def __init__(self, *args, task=current_task, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._task = task

    async def get_async_scoped_session(
        self,
    ) -> async_scoped_session[AlchemyAsyncSession | Any]:
        return async_scoped_session(
            session_factory=self._async_session_factory,
            scopefunc=self._task,
        )


class AsyncContextScopedSession(BaseAsyncSession):
    def __init__(self, *args, task=current_task, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._task = task
        self._async_scoped_session = None

    async def __aenter__(self):
        self._async_scoped_session = async_scoped_session(
            session_factory=self._async_session_factory,
            scopefunc=self._task,
        )
        return self._async_scoped_session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type in self.ERROR_EXC_TYPES:
            await self._async_scoped_session.rollback()

        await self._async_scoped_session.close()


def get_async_engine(url_: str | URL, echo: bool, poolclass_) -> AsyncEngine:
    """
    Async engine sqlalchemy.

    :param str | URL url_:
    :param bool echo:
    :param poolclass_:
    :return AsyncEngine:
    """
    return create_async_engine(
        url=url_, echo=echo, poolclass=poolclass_, pool_pre_ping=True
    )


URL_ = URL.create(
    drivername=config.postgres_driver_name,
    database=config.postgres_db,
    username=config.postgres_user,
    password=config.postgres_password,
    host=config.postgres_host,
    port=config.postgres_port,
)

engine_ = get_async_engine(url_=URL_, echo=False, poolclass_=NullPool)
scoped_session = AsyncScopedSession(async_engine=engine_)
async_contextmanager_session = AsyncContextScopedSession(async_engine=engine_)


async def async_session() -> (
    Coroutine[Any, Any, async_scoped_session[AlchemyAsyncSession]]
):
    """
    Получение async session DB.

    :return Coroutine[Any, Any, async_scoped_session[AlchemyAsyncSession]]:
    """
    return scoped_session.get_async_scoped_session()
