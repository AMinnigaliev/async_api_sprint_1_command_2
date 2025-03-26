import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base


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
        "User", secondary="user_subscriptions", back_populates="subscriptions"
    )

    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Role {self.name}>"
