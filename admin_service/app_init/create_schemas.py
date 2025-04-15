import asyncio
import os

import psycopg2


async def create_schemas() -> None:
    """Функция создания схемы admin в postgres."""
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


async def main():
    await create_schemas()


if __name__ == "__main__":
    asyncio.run(main())
