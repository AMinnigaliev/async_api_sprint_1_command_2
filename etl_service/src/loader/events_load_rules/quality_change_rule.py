from models.events.clickhouse_models import QualityChangeEventModel


class QualityChangeEventRule:

    def __init__(self, event_data: dict) -> None:
        self._event_data = event_data

    def execute(self) -> QualityChangeEventModel:
        return (
            QualityChangeEventModel(
                user_id=self._event_data.get("user_id"),
                timestamp=self._event_data.get("timestamp"),
                video_id=self._event_data.get("video_id"),
                old_quality=self._event_data.get("old_quality"),
                new_quality=self._event_data.get("new_quality"),
            )
        )
