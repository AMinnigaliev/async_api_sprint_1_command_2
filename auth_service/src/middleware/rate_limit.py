from redis.asyncio import Redis
from redis.asyncio.client import Pipeline
from limits import parse
from limits.storage import RedisStorage
from limits.strategies import FixedWindowRateLimiter
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.config import settings

__all__ = ["RateLimitMiddleware", "AsyncRateLimitMiddleware"]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """RateLimit с использованием limits. Синхронный, реализует стратегию ограничения с фиксированным окном."""

    def __init__(self, app) -> None:
        super().__init__(app=app)
        self._rate_limit = parse(settings.rate_limit)
        self._strategy = FixedWindowRateLimiter(
            storage=RedisStorage(
                uri=f"redis://{settings.redis_host}:{settings.redis_port}",
            ),
        )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response | None:
        client_id = request.client.host

        if not self._strategy.test(self._rate_limit, client_id):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="TOO MANY REQUESTS")

        self._strategy.hit(self._rate_limit, client_id)

        return await call_next(request)


class AsyncRateLimitMiddleware(BaseHTTPMiddleware):
    """Кастомный RateLimit. Асинхронный, реализует стратегию ограничения с фиксированным окном."""

    def __init__(self, app) -> None:
        super().__init__(app=app)
        self._redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"
        self._limit = settings.rate_limit
        self._window_sec = settings.rate_limit_window
        self._key_template = "ratelimit:{client_id}"

        self.__def_counter = 0

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response | None:
        client_id = request.headers.get("X-Forwarded-For", request.client.host)
        key_ = self._key_template.format(client_id=client_id)

        redis_client: Redis = await Redis.from_url(url=self._redis_url)
        try:
            current_count = await redis_client.get(name=key_)
            current_count = int(current_count) if current_count else self.__def_counter

            if current_count > self._limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="TOO MANY REQUESTS")

            pipe: Pipeline = await redis_client.pipeline()
            pipe.incr(name=key_)
            pipe.expire(name=key_, time=self._window_sec)
            await pipe.execute()

        finally:
            await redis_client.close()

        return await call_next(request)
