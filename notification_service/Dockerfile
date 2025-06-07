FROM python:3.12-slim

ENV C_FORCE_ROOT=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

# Команда по умолчанию (может быть переопределена в docker-compose)
CMD ["celery", "--app=celery_app", "worker", "--loglevel=info"]
