import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.postgres import Base

user_subscriptions = Table(
    'user_subscriptions',
    Base.metadata,
    Column(
        'user_id',
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    ),
    Column(
        'subscription_id',
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id"),
        primary_key=True,
    ),
)


class UserRoleEnum(str, Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    USER = "user"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    users = relationship(
        "User", secondary=user_subscriptions, back_populates="subscriptions"
    )

    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Role {self.name}>"


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
    password = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    role = Column(
        Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.USER
    )
    subscriptions = relationship(
        "Subscription", secondary=user_subscriptions, back_populates="users"
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
