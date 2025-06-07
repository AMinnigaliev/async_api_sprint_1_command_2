#!/bin/bash

set -e

echo "Запуск приложения NOTIFY_API_SERVICE..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$NOTIFY_API_SERVICE_PORT"