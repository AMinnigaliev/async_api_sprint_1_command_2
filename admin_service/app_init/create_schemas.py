import asyncio
import logging
import os

import psycopg2

logger = logging.getLogger(__name__)


async def create_schemas() -> None:
    """Функция создания схем admin, content и notify в postgres."""
    logger.info(
        "Начало работы скрипта по созданию схемы admin, content и notify."
    )

    dsn = (
        f"dbname={os.getenv('PG_NAME', 'name')} "
        f"user={os.getenv('PG_USER', 'user')} "
        f"password={os.getenv('PG_PASSWORD', 'password')} "
        f"host={os.getenv('PG_HOST', '127.0.0.1')} "
        f"port={os.getenv('PG_PORT', '5432')}"
    )
    conn = psycopg2.connect(dsn)
    conn.autocommit = True

    with conn.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS admin;")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS content;")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS notify;")

    conn.close()

    logger.info("Схемы созданы.")


async def main():
    await create_schemas()


if __name__ == "__main__":
    asyncio.run(main())
