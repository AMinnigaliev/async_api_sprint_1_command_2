#!/usr/bin/env bash

set -e

if [ ! -f /app/.init_done ]; then
    echo "Создание схемы admin, content и notify в postgres."
    python3 /app/app_init/create_schemas.py || { echo "Ошибка при выполнении create_schemas.py"; exit 1; }

    echo "Предварительные операции успешно выполнены."

    touch /app/.init_done
fi

echo "Запуск приложения..."

python manage.py migrate --no-input
python manage.py collectstatic --no-input

cp -r /app/static/. /var/www/static/

chown www-data:www-data /var/log

uwsgi --strict --ini /app/uwsgi/uwsgi.ini