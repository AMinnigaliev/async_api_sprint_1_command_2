import uuid

from extract.events.producer_rules.interface_ import AbstractEventRule
from models.events import VideoCompleteDC


class VideoCompleteEventRule(AbstractEventRule):

    def __init__(self, event_value: dict, event_key: str) -> None:
        super().__init__(event_value=event_value, event_key=event_key)
        self._video_complete_dc: VideoCompleteDC | None = None

    @property
    def video_complete_dc(self) -> VideoCompleteDC:
        if not self._video_complete_dc:
            self._video_complete_dc = VideoCompleteDC(
                user_id=self.event_value["user_id"],
                timestamp=self.event_value["timestamp"],
                video_id=self.event_value["data"]["video_id"],
                duration_total=self.event_value["data"]["duration_total"],
            )

        return self._video_complete_dc

    @property
    def event_storage_key(self) -> str:
        return f"{self.event_key}:{self.video_complete_dc.user_id}:{uuid.uuid4()}"

    def execute(self) -> tuple:
        event_storage_key = self.event_storage_key
        event_data = self.video_complete_dc.model_dump_json()

        return event_storage_key, event_data
