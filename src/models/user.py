import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from werkzeug.security import check_password_hash, generate_password_hash

from src.db.postgres import Base


class UserRoleEnum(str, Enum):
    SUPERUSER = "SUPERUSER"
    ADMIN = "admin"
    USER = "user"


# Промежуточная таблица для связи "многие ко многим"
user_subscriptions = Table(
    "user_subscriptions",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("subscription_id", UUID(as_uuid=True), ForeignKey("subscriptions.id"), primary_key=True),
)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", secondary=user_subscriptions, back_populates="subscriptions")

    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"<Subscription {self.name}>"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False, index=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    role = Column(SqlEnum(UserRoleEnum), nullable=False, default=UserRoleEnum.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)

    subscriptions = relationship("Subscription", secondary=user_subscriptions, back_populates="users")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")

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
        return f"<User {self.login}>"


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    login_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="login_history")

    def __repr__(self) -> str:
        return f"<LoginHistory user_id={self.user_id} login_time={self.login_time}>"
