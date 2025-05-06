from contextlib import contextmanager

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError, InterfaceError
from sqlalchemy.orm.scoping import scoped_session as ScopedSessionType

from core import config
from core.logger import logger
from utils.abstract import SingletonMeta


HTTP_URL = URL.create(
    drivername=config.clickhouse_http_driver_name,
    database=config.clickhouse_db,
    username=config.clickhouse_user,
    password=config.clickhouse_password,
    host=config.clickhouse_host,
    port=config.clickhouse_http_port,
)


class BaseSession(metaclass=SingletonMeta):
    ERROR_EXC_TYPES = [
        SQLAlchemyError,
        InterfaceError,
    ]

    def __init__(self, engine) -> None:
        self._engine = engine
        self._session_factory = sessionmaker(bind=engine)


class ScopedSession(BaseSession):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._scoped_session = None

    @property
    def scoped_session(self) -> ScopedSessionType:
        if not self._scoped_session:
            self._scoped_session = scoped_session(session_factory=self._session_factory)

        return self._scoped_session

    @property
    def session(self):
        return self.scoped_session()

    @contextmanager
    def context_session(self):
        try:
            yield self.session

        except self.ERROR_EXC_TYPES as ex:
            logger.error(f"SQLAlchemy(Clickhouse) error: {ex}")
            self.session.rollback()

        except Exception as ex:
            logger.error(f"Not correct SQLAlchemy(Clickhouse) error: {ex}")
            self.session.rollback()

        finally:
            self.session.close()


def get_engine(url_: str | URL, echo: bool, poolclass_):
    return create_engine(url=url_, echo=echo, poolclass=poolclass_, pool_pre_ping=True)


engine_ = get_engine(url_=HTTP_URL, echo=False, poolclass_=NullPool)
clickhouse_scoped_ = ScopedSession(engine=engine_)

clickhouse_session = clickhouse_scoped_.session
clickhouse_context_session = clickhouse_scoped_.context_session
