import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLAEnum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.postgres import Base
from src.models.subscription import Subscription
from src.models.user_subscription import user_subscriptions


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
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(UTC)
    )
    role = Column(
        SQLAEnum(UserRoleEnum), nullable=False, default=UserRoleEnum.USER
    )
    subscriptions = relationship(
        Subscription, secondary=user_subscriptions, back_populates="users"
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

    def __repr__(self) -> str:
        return f'<User {self.login}>'
