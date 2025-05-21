import logging
from flask import Flask
from .events.views import bp as events_bp
# Если позже потребуется фоновый scheduler (TTL‑чистка пар «page_view»),
# раскомментируйте строку ниже и добавьте реализацию в core.scheduler:
# from .core.scheduler import start as start_scheduler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


def create_app() -> Flask:
    """Фабрика приложения Flask для events_service."""
    app = Flask(__name__)

    # Регистрируем blueprint с эндпоинтом /events
    app.register_blueprint(events_bp)

    # При необходимости запускаем фоновые задачи
    # start_scheduler()

    return app


if __name__ == "__main__":
    application = create_app()
    # В продакшене запускайте Gunicorn/Uvicorn; эта строка — для локального
    # dev‑раннера
    application.run(host="0.0.0.0", port=5000)
