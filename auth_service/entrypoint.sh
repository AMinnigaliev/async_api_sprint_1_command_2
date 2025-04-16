#!/bin/bash

set -e

if [ ! -f /app/.init_done ]; then
    echo "Создание схемы auth в postgres."
    python3 /app/src/app_init/create_schemas.py || { echo "Ошибка при выполнении create_schemas.py"; exit 1; }
    echo "Применение миграций."
    # TODO: Дубль выполнения миграций (миграции так же выполняются в auth_service/src/db/init_postgres.py и movies_service/src/db/init_postgres.py)
#    alembic upgrade head
    echo "Запуск предварительных скриптов..."
    python3 /app/src/app_init/create_superuser.py || { echo "Ошибка при выполнении create_superuser.py"; exit 1; }
    touch /app/.init_done
    echo "Предварительные скрипты успешно выполнены."
fi

echo "Запуск приложения..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$AUTH_SERVICE_PORT"