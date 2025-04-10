import uuid
from datetime import UTC, datetime
from enum import Enum
from fastapi import HTTPException, status
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from src.core.security import verify_token
from src.db.postgres import Base
from src.models.login_history import LoginHistory
from werkzeug.security import check_password_hash, generate_password_hash


class UserRoleEnum(str, Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    oauth_provider = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    role = Column(
        SQLAEnum(UserRoleEnum), nullable=False, default=UserRoleEnum.USER
    )
    is_active = Column(Boolean, default=True, nullable=False)
    login_history = relationship(
        "LoginHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(
        self,
        login: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        role: UserRoleEnum = UserRoleEnum.USER,
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: UUID) -> "User":
        if user_id:
            if user := await db.get(cls, user_id):
                return user

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    @classmethod
    async def get_user_by_login(
        cls, db: AsyncSession, login: str
    ) -> "User | None":
        """
        Возвращает пользователя по логину.
        """
        result = await db.execute(select(cls).where(cls.login == login))
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_by_token(
        cls, db: AsyncSession, token: str
    ) -> "User | None":
        """
        Извлекает пользователя из JWT access-токена.
        """
        payload = verify_token(token)
        user_id = payload.get("user_id")

        return await cls.get_user_by_id(db, user_id)

    async def add_login_history(
            self, db: AsyncSession, user_agent: str = "unknown"
    ) -> None:
        """
        Добавляет запись входа в систему.
        """
        login_entry = LoginHistory(user_id=self.id, user_agent=user_agent)
        db.add(login_entry)
        await db.commit()

    async def get_login_history(self, db: AsyncSession, page_size: int, page_number: int) -> list[LoginHistory]:
        """
        Возвращает список истории входов пользователя.
        """
        offset = (page_number - 1) * page_size

        stmt = select(LoginHistory).where(LoginHistory.user_id == self.id).limit(page_size).offset(offset)
        result = await db.execute(stmt)

        return result.scalars().all()

    def __repr__(self) -> str:
        return f"<User {self.login}>"
