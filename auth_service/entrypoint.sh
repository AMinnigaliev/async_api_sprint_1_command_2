#!/bin/bash

set -e

# Проверяем, выполнена ли инициализация
if [ ! -f /app/.init_done ]; then
    echo "Запуск предварительных скриптов..."

    python3 /app/src/app_init/create_superuser.py || { echo "Ошибка при выполнении create_superuser.py"; exit 1; }
    touch /app/.init_done

    echo "Предварительные скрипты успешно выполнены."
fi

echo "Запуск приложения..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000