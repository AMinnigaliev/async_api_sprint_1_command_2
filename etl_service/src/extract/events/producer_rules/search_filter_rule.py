import uuid

from extract.events.producer_rules.interface_ import AbstractEventRule
from models.events import SearchFilterDC


class SearchFilterEventRule(AbstractEventRule):

    def __init__(self, event_value: dict, event_key: str) -> None:
        super().__init__(event_value=event_value, event_key=event_key)
        self._search_filter_dc: SearchFilterDC | None = None

    @property
    def search_filter_dc(self) -> SearchFilterDC:
        if not self._search_filter_dc:
            self._search_filter_dc = SearchFilterDC(
                user_id=self.event_value["user_id"],
                timestamp=self.event_value["timestamp"],
                search_query=self.event_value["data"]["search_query"],
                filters=self.event_value["data"]["filters"],
            )

        return self._search_filter_dc

    @property
    def event_storage_key(self) -> str:
        return f"{self.event_key}:{self.search_filter_dc.user_id}:{uuid.uuid4()}"

    def execute(self) -> tuple:
        event_storage_key = self.event_storage_key
        event_data = self.search_filter_dc.model_dump_json()

        return event_storage_key, event_data
