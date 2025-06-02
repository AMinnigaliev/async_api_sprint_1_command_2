from celery_app import app
from .default import DefaultTask
from .real_time.simple_task import SimpleSum

app.register_task(DefaultTask())

app.register_task(SimpleSum())
