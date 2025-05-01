from typing import TypeVar

from redis.asyncio import Redis

from core import config
from interface.storage.redis_storage import RedisStorage

__all__ = ["RedisContextManagerT", "RedisContextManager", "redis_context_manager"]

RedisContextManagerT = TypeVar("RedisContextManagerT", bound="RedisContextManager")


class RedisContextManager:
    """Контекстный менеджер по работе с RedisStorage."""

    URL_TEMPLATE = "redis://{}:{}"

    def __init__(self) -> None:
        self._redis_storage = None

    @property
    def redis_storage(self):
        return self._redis_storage

    async def __aenter__(self):
        redis_ = await Redis.from_url(
            url=self.URL_TEMPLATE.format(config.redis_host, config.redis_port),
            password=config.redis_password,
            db=config.redis_movies_db,
            decode_responses=True,
        )
        self._redis_storage = RedisStorage(redis_=redis_)

        return self._redis_storage

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._redis_storage.close_()


redis_context_manager = RedisContextManager()
