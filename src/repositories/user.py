from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.models.user import User


async def get_user_by_id(
    user_id: UUID, db: AsyncSession = Depends(get_session)
) -> User:
    if user := await db.get(User, user_id):
        return user

    raise HTTPException(status_code=404, detail="User not found")
