FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

# ── код приложения ───────────────────────────────────────────────
COPY src ./src
COPY entrypoint.sh /app/entrypoint.sh

# Удаляем возможные CR-символы и делаем файл исполняемым
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Абсолютный путь ← решает «exec format error»
ENTRYPOINT ["/app/entrypoint.sh"]
