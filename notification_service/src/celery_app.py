from celery import Celery

from core import celery_config
from beats_schedule.real_time import beats_schedule as beats_real_time
from beats_schedule.deferred import beats_schedule as beats_deferred


app = Celery(
    celery_config.service_name,
    broker=celery_config.broker_url,
    backend=celery_config.backend_url,
    beat_schedule={
        **beats_real_time,
        **beats_deferred,
    },
)
app.conf.update(
    task_serializer=celery_config.task_serializer,
    accept_content=celery_config.accept_content,
    result_serializer=celery_config.result_serializer,
    timezone=celery_config.timezone,
    enable_utc=celery_config.enable_utc,
    worker_prefetch_multiplier=celery_config.worker_prefetch_multiplier,
    worker_max_tasks_per_child=celery_config.worker_max_tasks_per_child,
    worker_max_memory_per_child=celery_config.worker_max_memory_per_child,
)

app.conf.task_queues = celery_config.task_queues
app.conf.task_routes = celery_config.task_routes
app.autodiscover_tasks(["tasks", ], force=True)

