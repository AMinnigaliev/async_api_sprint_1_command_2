from datetime import datetime, timedelta
from typing import Any

from celery import Task
from sqlalchemy.sql.base import elements

from celery_app import app
from core import logger, CeleryBaseException, celery_config
from models import DefaultTaskModel, TaskMetaModel


class DefaultTask(Task):
    """Базовая задача, распределяющая входящая задачи по задачам и очередям."""

    name = "default"

    def __init__(self) -> None:
        super().__init__()

        self._task_model: DefaultTaskModel | None = None

    def before_start(self, task_id: str, args, kwargs):
        meta_: dict[str, Any] = kwargs.get("meta", {})

        try:
            self._task_model = DefaultTaskModel(
                meta=TaskMetaModel(
                    task_id=task_id,
                    x_request_id=meta_.get("x-Request-Id"),  # TODO:
                    send_at=meta_.get("send_at"),
                    execution_at=meta_.get("execution_at"),
                    relevance_at=meta_.get("relevance_at"),
                ),
                delivery_methods=kwargs["delivery_methods"],
                task_name=kwargs["notification_type"],
                notification_data=kwargs.get("notification_data", {}),
            )

        except KeyError as ex:
            raise CeleryBaseException(f"Error execute TaskID={task_id}: not found param '{ex}'")

    def run(self, *args, **kwargs) -> None:
        try:
            tasks_kwargs = {
                "meta": {
                    "x_request_id": self._task_model.meta.x_request_id,
                    "relevance_at": self._task_model.meta.relevance_at,
                },
                "notification_data": self._task_model.notification_data,
                "delivery_methods": self._task_model.delivery_methods,
            }
            if execution_at := self._task_model.meta.execution_at:  # TODO:
                app.tasks[self._task_model.task_name].apply_async(
                    countdown=10,  # TODO:
                    queue=celery_config.real_time_group,
                    kwargs=tasks_kwargs,
                )

            else:
                app.tasks[self._task_model.task_name].apply_async(kwargs=tasks_kwargs)

            log_msg = (
                f"Create Task(UID: {self._task_model.meta.task_id}, name:'{self._task_model.task_name}'); "
                f"x_request_id: {self._task_model.meta.x_request_id}; "
                f"execution_at: {self._task_model.meta.execution_at}; send_at: {self._task_model.meta.send_at}"
            )
            logger.info(log_msg)

        except CeleryBaseException as ex:
            logger.error(f"Error apply Task{self._task_model.meta.task_id}(name: '{self._task_model.task_name}'): {ex}")
