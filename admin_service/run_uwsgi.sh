#!/usr/bin/env bash

set -e

python manage.py migrate --no-input

python manage.py collectstatic --no-input

cp -r /opt/app/static/. /var/www/static/

chown www-data:www-data /var/log

uwsgi --strict --ini /opt/app/uwsgi/uwsgi.ini
