#!/bin/bash

set -e

echo "Запуск приложения SHORT_URL_SERVICE..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$SHORT_URL_SERVICE_PORT"