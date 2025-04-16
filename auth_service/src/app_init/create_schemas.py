import asyncio
import logging.config

from sqlalchemy import text

from src.core.logger import LOGGING
from src.db.postgres import engine

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def create_auth_schema() -> None:
    """Функция создания схемы auth в postgres."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth;"))


async def main():
    await create_auth_schema()


if __name__ == "__main__":
    asyncio.run(main())
