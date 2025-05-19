#!/bin/bash

set -e

echo "Запуск приложения..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$USER_ACTIVITY_SERVICE_PORT"