import asyncio
import json
from typing import Any, AsyncGenerator

import aiohttp
from celery import Task
from jinja2 import Template

from core import celery_config, CeleryBaseException, logger
from models import DefaultTaskModel, TaskMetaModel
from utils.rmq_client import AsyncRabbitMQClient


class AdminInfoMessage(Task):
    """Информационное сообщение от администратора для пользователей"""

    name = "admin_info_message"
    queue = celery_config.real_time_group

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
            self._template = celery_config.jinja_template_env.get_template("admin_info_message.html")

        return self._template

    @property
    def need_email_notification(self) -> bool:
        return "email" in self.task_model.delivery_methods

    @property
    def need_webpush_notification(self) -> bool:
        return "webpush" in self.task_model.delivery_methods

    @property
    def rmq_email_client(self):
        return AsyncRabbitMQClient(
            amqp_url=celery_config.rmq_url,
            queue_name=celery_config.email_queue_name,
        )

    @property
    def rmq_webpush_client(self):
        return AsyncRabbitMQClient(
            amqp_url=celery_config.rmq_url,
            queue_name=celery_config.webpush_queue_name,
        )

    def before_start(self, task_id: str, args, kwargs):
        self._task_model = None
        self._template = None

        meta_: dict[str, Any] = kwargs.get("meta", {})

        try:
            self._task_model = DefaultTaskModel(
                meta=TaskMetaModel(
                    task_id=task_id,
                    x_request_id=meta_.get("x-Request-Id"),
                    send_at=meta_.get("send_at"),
                    execution_at=meta_.get("execution_at"),
                    relevance_at=meta_.get("relevance_at"),
                ),
                delivery_methods=kwargs["delivery_methods"],
                notification_data=kwargs["notification_data"],
                task_name=self.name,
            )

        except KeyError as ex:
            raise CeleryBaseException(f"Error execute TaskName={self.name}: not found param '{ex}'")

    def run(self, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(self.run_async())

    async def run_async(self):
        template_data = self.task_model.template_data
        base_render_data = {"title": template_data["title"], "body": template_data["body"]}

        output_data_by_users = dict()
        async for user_info in self._get_user_info():
            user_render_data = {
                "username": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
                "user_id": user_info["id"],
                **base_render_data,
            }
            output_data_by_users[user_info["id"]] = self.template.render(user_render_data)

            if output_data_by_users and len(output_data_by_users.keys()) >= self.CHUNK:
                await self._notify(data_for_notification=output_data_by_users)
                output_data_by_users = dict()

        if output_data_by_users:
            await self._notify(data_for_notification=output_data_by_users)

    async def _get_user_info(
        self,
        start_page: int = 1,
        page_size: int = 2_000,
        max_pages: int | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        url = f"{celery_config.auth_service_url}/{celery_config.auth_service_get_users_info_uri}"
        payload = {"user_ids": self.task_model.user_ids} if self.task_model.user_ids else {}
        current_page = start_page
        total_pages = None

        async with aiohttp.ClientSession() as session:
            while True:
                if max_pages is not None and current_page > max_pages:
                    break

                params = {"page_number": current_page, "page_size": page_size}

                try:
                    async with session.post(url=url, params=params, json=payload, timeout=10) as response:
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

        if self.need_email_notification:
            try:
                await self.rmq_email_client.connect()
                await self.rmq_email_client.publish(base_message_body, headers=self.rmq_email_client.DEF_HEADERS)

            finally:
                await self.rmq_email_client.disconnect()

        if self.need_webpush_notification:
            try:
                await self.rmq_webpush_client.connect()
                await self.rmq_webpush_client.publish(
                    base_message_body,
                    headers=self.rmq_webpush_client.DEF_HEADERS,
                )

            finally:
                await self.rmq_webpush_client.disconnect()
