from celery.schedules import crontab


beats_schedule = {
    "most_popular_movies_of_week": {
        'task': 'most_popular_movies_of_week',
        'schedule': crontab(hour=9, minute=30, day_of_week="1"),
    },
}
