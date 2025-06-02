from celery import Task

from core import celery_config

class SimpleSum(Task):

    name = "simple_task"
    queue = celery_config.real_time_group

    def run(self, *args, **kwargs):
        a_ = kwargs.get("first", 1)
        b_ = kwargs.get("second", 1)

        return a_ + b_
