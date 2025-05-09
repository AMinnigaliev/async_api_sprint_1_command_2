from models.events.clickhouse_models import VideoCompleteEventModel


class VideoCompleteEventRule:

    def __init__(self, event_data: dict) -> None:
        self._event_data = event_data

    def execute(self) -> VideoCompleteEventModel:
        return (
            VideoCompleteEventModel(
                user_id=self._event_data.get("user_id"),
                timestamp=self._event_data.get("timestamp"),
                video_id=self._event_data.get("video_id"),
                duration_total=int(self._event_data.get("duration_total")),
            )
        )
