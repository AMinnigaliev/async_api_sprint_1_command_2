import asyncio
import json
from typing import Any

from celery import Task
from jinja2 import Template

from core import celery_config, CeleryBaseException
from models import DefaultTaskModel, TaskMetaModel
from utils.rmq_client import AsyncRabbitMQClient


class AdminInfoMessage(Task):
    """Информационное сообщение от администратора для пользователей"""

    name = "admin_info_message"
    queue = celery_config.real_time_group

    def __init__(self) -> None:
        super().__init__()

        self._task_model: DefaultTaskModel | None = None
        self._template: Template | None = None
        self._rmq_client: AsyncRabbitMQClient | None = None

    @property
    def task_model(self) -> DefaultTaskModel | None:
        return self._task_model

    @property
    def template(self):
        if not self._template:
            self._template = celery_config.template_env.get_template("admin_info_message.html")

        return self._template

    @property
    def need_email_notification(self) -> bool:
        return "email" in self.task_model.delivery_methods

    @property
    def need_webpush_notification(self) -> bool:
        return "webpush" in self.task_model.delivery_methods

    @property
    def rmq_email_client(self):
        if not self._rmq_client:
            self._rmq_client = AsyncRabbitMQClient(
                amqp_url=celery_config.rmq_url,
                queue_name=celery_config.email_queue_name,
            )

        return self._rmq_client

    @property
    def rmq_webpush_client(self):
        if not self._rmq_client:
            self._rmq_client = AsyncRabbitMQClient(
                amqp_url=celery_config.rmq_url,
                queue_name=celery_config.webpush_queue_name,
            )

        return self._rmq_client

    def before_start(self, task_id: str, args, kwargs):
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
            )

        except KeyError as ex:
            raise CeleryBaseException(f"Error execute TaskName={self.name}: not found param '{ex}'")

    def run(self, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(self.run_async())

    async def run_async(self):
        template_data = self.task_model.template_data

        base_render_data = {"title": template_data["title"], "body": template_data["body"]}
        username_by_ids = await self._get_username_by_ids(user_ids=self.task_model.user_ids)

        output_data_by_users = dict()
        for user_id, username in username_by_ids.items():
            user_render_data = {"username": username, "user_id": user_id, **base_render_data}
            output_data_by_users[user_id] = self.template.render(user_render_data)

        await self._notify(data_for_notification=output_data_by_users)

    async def _get_username_by_ids(self, user_ids: list[str]) -> dict[str, str]:  # TODO:
        return {id_: "qweasd" for id_ in user_ids}

    async def _notify(self, data_for_notification: dict[str, str]):
        q = 1
        base_message_body = json.dumps(
            {
                **self.task_model.meta.model_dump(mode="json"),
                "message_body": data_for_notification,
            }
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
