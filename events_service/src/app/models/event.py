'''Определение простой схемы входящих событий для Events Service.'''
from typing import Optional

from pydantic import BaseModel


class EventSchema(BaseModel):
    """Простая модель для валидации входящих событий.

    Проверяются только три поля:
      - event: любой строковый идентификатор события
      - token: строка или None
      - data: любой словарь с полезной нагрузкой события
    """
    event: str
    token: Optional[str] = None
    data: dict

    def to_dict(self) -> dict:
        """Алиас для сериализации модели в словарь."""
        return self.dict()
