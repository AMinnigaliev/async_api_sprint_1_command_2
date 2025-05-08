#!/bin/sh
set -e

python3 /app/db/clickhouse_migration/migrate.py
python3 /app/run.py