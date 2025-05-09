import asyncio
import logging
import os

import psycopg2

logger = logging.getLogger(__name__)


async def create_schemas() -> None:
    """Функция создания схем admin и content в postgres."""
    logger.info("Начало работы скрипта по созданию схемы admin и content.")

    dsn = (
        f"dbname={os.getenv('PG_NAME')} "
        f"user={os.getenv('PG_USER')} "
        f"password={os.getenv('PG_PASSWORD')} "
        f"host={os.getenv('PG_HOST')} "
        f"port={os.getenv('PG_PORT', '5432')}"
    )
    conn = psycopg2.connect(dsn)
    conn.autocommit = True

    with conn.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS admin;")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS content;")

    conn.close()

    logger.info("Схемы созданы.")


async def main():
    await create_schemas()


if __name__ == "__main__":
    asyncio.run(main())
