import json
import asyncio
from typing import Any, AsyncGenerator

import aiohttp
from celery import Task
from jinja2 import Template

from core import celery_config, logger
from models import DefaultTaskModel, TaskMetaModel
from utils.rmq_client import AsyncRabbitMQClient


class MostPopularMoviesOfWeek(Task):
    """Отложенная задача: оповещение пользователей о самых популярных фильмах на этой недели."""

    name = "most_popular_movies_of_week"
    queue = celery_config.deferred_group

    MIN_COUNT_MOVIES = 5
    MAX_COUNT_MOVIES = 15
    CHUNK = 500

    def __init__(self) -> None:
        super().__init__()

        self._task_model: DefaultTaskModel | None = None
        self._template: Template | None = None

    @property
    def task_model(self) -> DefaultTaskModel | None:
        return self._task_model

    @property
    def template(self):
        if not self._template:
            self._template = celery_config.jinja_template_env.get_template("most_popular_movies_of_week.html")

        return self._template

    @property
    def rmq_email_client(self):
        return AsyncRabbitMQClient(
            amqp_url=celery_config.rmq_url,
            queue_name=celery_config.email_queue_name,
        )

    def before_start(self, task_id: str, args, kwargs):
        self._task_model = None
        self._template = None

        self._task_model = DefaultTaskModel(meta=TaskMetaModel(task_id=task_id), task_name=self.name)

    def run(self, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(self.run_async())

    async def run_async(self):
        most_popular_movies_by_rating = await self._get_movies_by_rating()
        count_movies = len(most_popular_movies_by_rating)

        if count_movies >= self.MIN_COUNT_MOVIES:
            output_data_by_users = dict()

            async for user_info in self._get_user_info():
                try:
                    user_render_data = {
                        "top_count": count_movies,
                        "username": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
                        "movies": most_popular_movies_by_rating,
                    }
                    output_data_by_users[user_info["id"]] = self.template.render(user_render_data)

                except KeyError as ex:
                    logger.warning(f"error get info(user_info: {user_info}): {ex}")

                if output_data_by_users and len(output_data_by_users.keys()) >= self.CHUNK:
                    await self._notify(data_for_notification=output_data_by_users)
                    output_data_by_users = dict()

            if output_data_by_users:
                await self._notify(data_for_notification=output_data_by_users)

        else:
            logger.info(f"not found necessary most popular movies count ({count_movies} < {self.MIN_COUNT_MOVIES})")

    async def _get_movies_by_rating(self) -> list[dict[str, int]]:
        params = {"page_number": 1, "page_size": self.MAX_COUNT_MOVIES}
        payload = {
            "query": {},
            "sort": [
                {"imdb_rating": { "order": "desc" }},
            ],
        }
        url = f"{celery_config.movies_service_url}/{celery_config.movies_service_film_search_internal_uri}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, params=params, json=payload, timeout=10) as response:
                    movies =  await response.json()

                    return [
                        {"title": m["title"], "rating": m["imdb_rating"], "id": m.get("uuid", "")}
                        for m in movies if m.get("title") and  m.get("imdb_rating")
                    ] if movies else []

        except (asyncio.TimeoutError, asyncio.CancelledError) as ex:
            logger.error(f"Error get top movies: {ex}")
            return []

    @staticmethod
    async def _get_user_info(
        start_page: int = 1,
        page_size: int = 2_000,
        max_pages: int | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        url = f"{celery_config.auth_service_url}/{celery_config.auth_service_get_users_info_uri}"
        current_page = start_page
        total_pages = None

        async with aiohttp.ClientSession() as session:
            while True:
                if max_pages is not None and current_page > max_pages:
                    break

                params = {"page_number": current_page, "page_size": page_size}

                try:
                    async with session.post(url=url, params=params, timeout=10) as response:
                        response_data: dict[str, Any] =  await response.json()
                        meta_: dict[str, str | int] = response_data.get("meta", {})
                        users_info: list[dict[str, Any]] = response_data.get("users", [])

                        if users_info:
                            for user_info in users_info:
                                yield user_info

                        else:
                            break

                        if total_pages is None and "total_pages" in meta_:
                            total_pages = meta_["total_pages"]

                        if total_pages is not None and current_page >= total_pages:
                            break

                        current_page += 1
                        await asyncio.sleep(1.0)

                except (asyncio.TimeoutError, asyncio.CancelledError, aiohttp.ClientError) as ex:
                    logger.error(f"Error get users: {ex}")
                    break

                except Exception as ex:
                    logger.error(f"not correct_error: {ex}")
                    break

    async def _notify(self, data_for_notification: dict[str, str]):
        base_message_body = json.dumps(
            {
                **self.task_model.meta.model_dump(mode="json"),
                "message_body": data_for_notification,
            },
        )

        try:
            await self.rmq_email_client.connect()
            await self.rmq_email_client.publish(base_message_body, headers=self.rmq_email_client.DEF_HEADERS)

        finally:
            await self.rmq_email_client.disconnect()
