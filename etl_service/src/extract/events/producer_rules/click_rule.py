import uuid
from asyncio import iscoroutinefunction

from core.logger import logger
from extract.events.producer_rules.interface_ import AbstractEventRule
from models.events.element_click import (ClickElementDC,
                                         ClickElementPlayMovies,
                                         ClickElementsTypesEnum)
from utils import EventRuleError


class ElementClickEventRule(AbstractEventRule):

    def __init__(self, event_value: dict, event_key: str) -> None:
        super().__init__(event_value=event_value, event_key=event_key)
        self._click_element_dc: ClickElementDC | None = None

    @property
    def click_element_dc(self) -> ClickElementDC:
        if not self._click_element_dc:
            data = {
                "user_id": self.event_value.get("user_id"),
                "timestamp": self.event_value.get("timestamp"),
                "element_type": self.event_value["data"].get(
                    "element_type"
                ) if self.event_value.get("data") else None,
            }
            data.update({key_: value_ for key_, value_ in self.event_value.get(
                "data", {}
            ).items()})

            self._click_element_dc = ClickElementDC(
                element_type=self.event_value["data"].get(
                    "element_type"
                ) if self.event_value.get("data") else None,
                user_id=self.event_value.get("user_id"),
                timestamp=self.event_value.get("timestamp"),
                data=data,
            )

        return self._click_element_dc

    @property
    def event_storage_key(self) -> str:
        return (
            f"{self.event_key}:{self.click_element_dc.element_type}:"
            f"{self.click_element_dc.user_id}:{uuid.uuid4()}"
        )

    @property
    def element_type_executors(self) -> dict:
        return {
            ClickElementsTypesEnum.play_movies_element.name:
                self._click_element_play_movies,
        }

    async def execute(self) -> tuple:
        event_storage_key, event_data = None, None

        if element_type_executor := self.element_type_executors.get(
                self.click_element_dc.element_type
        ):
            try:
                if iscoroutinefunction(element_type_executor):
                    (
                        event_storage_key, event_data
                    ) = await element_type_executor()

                else:
                    event_storage_key, event_data = element_type_executor()

            except EventRuleError as ex:
                logger.warning(
                    f"ElementClickEvent: error(element_type="
                    f"{self.click_element_dc.element_type}): {ex}"
                )

        else:
            logger.warning(
                f"ElementClickEvent: not found executor for "
                f"element_type='{self.click_element_dc.element_type}'"
            )

        return event_storage_key, event_data

    def _click_element_play_movies(self) -> tuple:
        try:
            event_data = ClickElementPlayMovies(**self.click_element_dc.data)

            return self.event_storage_key, event_data.model_dump_json()

        except TypeError as ex:
            logger.warning(
                f"ElementClickEvent error(element_type="
                f"{self.click_element_dc.element_type}): {ex}"
            )

        return None, None
