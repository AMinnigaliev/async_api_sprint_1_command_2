from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


async def get_user_by_login(db: AsyncSession, login: str) -> User:
    result = await db.execute(select(User).filter_by(login=login))
    if user:= result.scalars().first():
        return user

    raise HTTPException(status_code=404, detail="User not found")


async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User:
    if user := await db.get(User, user_id):
        return user

    raise HTTPException(status_code=404, detail="User not found")
