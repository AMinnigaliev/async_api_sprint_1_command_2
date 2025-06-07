#!/usr/bin/env bash
set -e

echo "⏳ Waiting for RabbitMQ…"
until nc -z "$RABBIT_HOST" "$RABBIT_PORT"; do
  echo "RabbitMQ unavailable, sleeping…"
  sleep 1
done

echo "🚀 Starting WebSocket-Sender"
exec uvicorn src.main:app --host 0.0.0.0 --port "${WEBSOCKET_SENDER_PORT:-8004}"
