import uuid

from extract.events.producer_rules.interface_ import AbstractEventRule
from models.events import PageViewDC


class PageViewEventRule(AbstractEventRule):

    def __init__(self, event_value: dict, event_key: str) -> None:
        super().__init__(event_value=event_value, event_key=event_key)
        self._page_view_dc: PageViewDC | None = None

    @property
    def page_view_dc(self) -> PageViewDC:
        if not self._page_view_dc:
            self._page_view_dc = PageViewDC(
                user_id=self.event_value["user_id"],
                timestamp=self.event_value["timestamp"],
                element_page_type=self.event_value["data"]["element_page_type"],
                page_number=self.event_value["data"]["page_number"],
            )

        return self._page_view_dc

    @property
    def event_storage_key(self) -> str:
        return f"{self.event_key}:{self.page_view_dc.user_id}:{uuid.uuid4()}"

    def execute(self) -> tuple:
        event_storage_key = self.event_storage_key
        event_data = self.page_view_dc.model_dump_json()

        return event_storage_key, event_data
