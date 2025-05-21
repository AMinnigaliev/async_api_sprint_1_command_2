import uuid

from extract.events.producer_rules.interface_ import AbstractEventRule
from models.events import QualityChangeDC


class QualityChangeEventRule(AbstractEventRule):

    def __init__(self, event_value: dict, event_key: str) -> None:
        super().__init__(event_value=event_value, event_key=event_key)
        self._quality_change_dc: QualityChangeDC | None = None

    @property
    def quality_change_dc(self) -> QualityChangeDC:
        if not self._quality_change_dc:
            self._quality_change_dc = QualityChangeDC(
                user_id=self.event_value["user_id"],
                timestamp=self.event_value["timestamp"],
                video_id=self.event_value["data"]["video_id"],
                old_quality=self.event_value["data"]["old_quality"],
                new_quality=self.event_value["data"]["new_quality"],
            )

        return self._quality_change_dc

    @property
    def event_storage_key(self) -> str:
        return (
            f"{self.event_key}:{self.quality_change_dc.user_id}:{uuid.uuid4()}"
        )

    def execute(self) -> tuple:
        event_storage_key = self.event_storage_key
        event_data = self.quality_change_dc.model_dump_json()

        return event_storage_key, event_data
