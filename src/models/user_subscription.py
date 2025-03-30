from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

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
