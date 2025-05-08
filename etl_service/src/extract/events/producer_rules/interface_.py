from abc import ABC, abstractmethod


class AbstractEventRule(ABC):
    """Класс-интерфейс для обработки события."""

    ANONYMOUS_USER = "anonymous"

    def __init__(self, event_value: dict, event_key: str) -> None:
        self._event_value = event_value
        self._event_key = event_key

    @property
    def event_value(self) -> dict:
        return self._event_value

    @property
    def event_key(self) -> str:
        return self._event_key

    @abstractmethod
    async def execute(self, *args, **kwargs) -> tuple:
        """Метод-обработчик события."""
