from celery_app import app
from .default import DefaultTask
from .real_time.admin_info_message import AdminInfoMessage

# Default
app.register_task(DefaultTask())

# RealTimeQueue
app.register_task(AdminInfoMessage())
