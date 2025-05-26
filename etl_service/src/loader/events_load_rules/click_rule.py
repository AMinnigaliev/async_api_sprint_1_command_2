from models.events.clickhouse_models import ClickElementEventModel


class ElementClickEventRule:

    def __init__(self, event_data: dict) -> None:
        self._event_data = event_data

    @property
    def unic_click_event_models(self) -> dict:
        return {}

    def execute(self):
        if event_model_executor := self.unic_click_event_models.get(
                self._event_data.get("element_type")
        ):
            return event_model_executor()

        else:
            return self._default_event_model_executor()

    def _default_event_model_executor(self) -> ClickElementEventModel:
        return (
            ClickElementEventModel(
                user_id=self._event_data.get("user_id"),
                page_type=self._event_data.get("page_type"),
                element_type=self._event_data.get("element_type"),
                timestamp=self._event_data.get("timestamp"),
            )
        )
