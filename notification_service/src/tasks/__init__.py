from celery_app import app
from .default import DefaultTask
from .real_time.admin_info_message import AdminInfoMessage
from .deferred.most_popular_movies_of_week import MostPopularMoviesOfWeek

# Default
app.register_task(DefaultTask())

# RealTimeQueue
app.register_task(AdminInfoMessage())

# DeferredQueue
app.register_task(MostPopularMoviesOfWeek())
