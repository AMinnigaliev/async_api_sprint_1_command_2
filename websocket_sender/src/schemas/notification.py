from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field, AwareDatetime

class DeliveryMessage(BaseModel):
    """Сообщение из RabbitMQ (пример на фото)."""
    task_id: str
    x_request_id: str | None = None
    send_at: AwareDatetime | None = None
    execution_at: AwareDatetime | None = None
    relevance_at: AwareDatetime | None = None
    message_body: Dict[str, str] = Field(
        ..., description="user_id: html-body"
    )
