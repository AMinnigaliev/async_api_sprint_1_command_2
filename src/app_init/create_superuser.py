import asyncio
import logging
import os

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.postgres import get_session
from src.models.user import User, UserRoleEnum

load_dotenv()
logger = logging.getLogger(__name__)


async def create_superuser(db: AsyncSession = Depends(get_session)) -> None:
    """Функция для создания суперпользователя."""
    logger.info("Начало работы скрипта по созданию суперпользователя.")

    superuser = User(
        login=os.getenv("SUPERUSER_NAME"),
        password=os.getenv("SUPERUSER_PASSWORD"),
        role=UserRoleEnum.SUPERUSER,
    )
    try:
        db.add(superuser)
        await db.commit()

    except settings.SQL_EXCEPTIONS as e:
        logger.error("Ошибка при добавлении суперпользователя: %s", e)
        raise

    logger.info("Суперпользователь создан.")


if __name__ == "__main__":
    asyncio.run(create_superuser())
