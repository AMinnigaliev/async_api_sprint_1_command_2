import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    login_time = Column(
        DateTime(timezone=True), nullable=False, default=datetime.now(UTC)
    )
    user_agent = Column(String(512), nullable=False, default="unknown")

    user = relationship("User", back_populates="login_history")

    def __repr__(self) -> str:
        return (
            f"<LoginHistory user_id={self.user_id} "
            f"login_time={self.login_time}>"
        )
