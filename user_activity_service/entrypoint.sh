#!/bin/bash

set -e

if [ ! -f /app/.init_done ]; then
    echo "Инициализация шардированного кластера MongoDB..."
    python3 /app/src/app_init/init_mongo_sharding.py || { echo "Ошибка при выполнении init_mongo_sharding.py"; exit 1; }

    echo "Инициализация MongoDB успешно выполнены."

    touch /app/.init_done
fi

echo "Запуск приложения USER_ACTIVITY_SERVICE..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$USER_ACTIVITY_SERVICE_PORT"