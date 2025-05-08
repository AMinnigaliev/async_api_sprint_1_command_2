#!/bin/sh
set -e

echo "⏳ Ждём Kafka и Redis…"

# ждём Kafka
until python3 - <<'EOF'
from kafka import KafkaConsumer
import time
import sys

try:
    consumer = KafkaConsumer(
        bootstrap_servers='kafka:9092',
        request_timeout_ms=1000,
        consumer_timeout_ms=1000
    )
    consumer.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
EOF
do
  echo "– Kafka недоступен, ждём…"
  sleep 1
done

echo "Kafka в сети."
echo "Стартуем приложение…"

exec gunicorn -w 4 -k gthread \
     'events_service.src.app.main:create_app()' \
     --bind 0.0.0.0:${PORT:-5000}

