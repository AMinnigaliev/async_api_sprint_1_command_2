import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import select

from src.core.config import settings
from src.db.init_postgres import create_database
from src.db.postgres import async_session
from src.models.user import User, UserRoleEnum

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def create_superuser() -> None:
    """Функция для создания суперпользователя."""
    logger.info("Проверка наличия логина и пароля суперпользователя.")

    login = os.getenv("SUPERUSER_NAME"),
    password = os.getenv("SUPERUSER_PASSWORD")

    if not login or not password:
        logger.error(
            "Нет логина или пароля суперпользователя. "
            "Суперпользователь не будет создан."
        )
        sys.exit()

    logger.info("Начало работы скрипта по созданию суперпользователя.")

    async with async_session() as db:
        existing_user = await db.execute(
            select(User).where(User.login == login)
        )
        if existing_user.scalars().first():
            logger.info("Суперпользователь уже существует.")
            return

        superuser = User(
            login=login,
            password=password,
            role=UserRoleEnum.SUPERUSER,
        )

        try:
            db.add(superuser)
            await db.commit()

        except settings.SQL_EXCEPTIONS as e:
            logger.error("Ошибка при добавлении суперпользователя: %s", e)
            await db.rollback()
            raise

    logger.info("Суперпользователь создан.")


async def main():
    await create_database()
    await create_superuser()


if __name__ == "__main__":
    asyncio.run(main())
