from models.events.clickhouse_models import PageViewModel


class PageViewEventRule:

    def __init__(self, event_data: dict) -> None:
        self._event_data = event_data

    def execute(self) -> PageViewModel:
        return (
            PageViewModel(
                user_id=self._event_data.get("user_id"),
                timestamp=self._event_data.get("timestamp"),
                element_page_type=self._event_data.get("element_page_type"),
                page_number=self._event_data.get("page_number"),
            )
        )
