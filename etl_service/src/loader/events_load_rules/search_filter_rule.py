from models.events.clickhouse_models import SearchFilterEventModel


class SearchFilterEventRule:

    def __init__(self, event_data: dict) -> None:
        self._event_data = event_data

    def execute(self) -> SearchFilterEventModel:
        return (
            SearchFilterEventModel(
                user_id=self._event_data.get("user_id"),
                timestamp=self._event_data.get("timestamp"),
                search_query=self._event_data.get("search_query"),
                filters=self._event_data.get("filters"),
            )
        )
