FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . /app
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
