# базовый слой с колёсами
FROM python:3.12-slim AS builder
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels -r requirements.txt

# runtime
FROM python:3.12-slim
WORKDIR /code
ENV PYTHONUNBUFFERED=1

# ставим только из колёс — binary-скрипты попадут в /usr/local/bin
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* && rm -rf /wheels

# копируем код и entrypoint
COPY src ./events_service/src
COPY entrypoint.sh .

# делаем точку входа
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
