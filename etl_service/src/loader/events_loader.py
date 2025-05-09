import json
from asyncio import iscoroutinefunction

from core import config
from core.logger import logger
from interface import RedisStorage_T
from models.events import EventsEnum
from loader.events_load_rules import (
    ElementClickEventRule,
    QualityChangeEventRule,
    VideoCompleteEventRule,
    SearchFilterEventRule,
    PageViewEventRule,
)


class Loader:
    """Класс по загрузке событий в ClickHouse."""

    def __init__(self, _clickhouse_session, redis_storage: RedisStorage_T):
        self._redis_storage: RedisStorage_T = redis_storage
        self._clickhouse_session = _clickhouse_session

    @property
    def redis_storage(self) -> RedisStorage_T:
        return self._redis_storage

    @property
    def clickhouse_session(self):
        return self._clickhouse_session

    @property
    def event_types(self) -> list:
        return [event.value for event in EventsEnum]

    async def run(self) -> None:
        """
        Точка запуска. Этапы:

        :return None:
        """
        for event_type in self.event_types:
            event_entities_lst = list()
            events_keys = await self.redis_storage.scan_iter(f"{event_type}:*")

            if events_keys:
                logger.debug(f"EventType '{event_type}' start Load to ClickHouse(count: {len(events_keys)})")

            for event_key in events_keys:
                event_data = await self._get_event_data_by_key(event_key=event_key)
                load_rule = self._get_load_rule_by_event_type(event_key=event_key)

                if event_data and load_rule:
                    if event_entities := await self._execute_load_rule(load_rule=load_rule, event_data=event_data):
                        event_entities_lst.append(event_entities)

            if len(event_entities_lst) >= config.etl_events_select_limit:
                self.clickhouse_session.insert(event_entities_lst)
                event_entities_lst.clear()

            if events_keys:
                await self._delete_events_from_storage(keys=events_keys, event_type=event_type)

    async def _get_event_data_by_key(self, event_key: str) -> dict:
        event_data = await self.redis_storage.retrieve_state(key_=event_key)

        return json.loads(event_data)

    @staticmethod
    def _get_load_rule_by_event_type(event_key: str):
        event_type = event_key.split(":")[0]
        event_loaders_by_types = {
            EventsEnum.ELEMENT_CLICK.value: ElementClickEventRule,
            EventsEnum.PAGE_VIEW.value: PageViewEventRule,
            EventsEnum.QUALITY_CHANGE.value: QualityChangeEventRule,
            EventsEnum.VIDEO_COMPLETE.value: VideoCompleteEventRule,
            EventsEnum.SEARCH_FILTER.value: SearchFilterEventRule,
        }

        return event_loaders_by_types.get(event_type)

    @staticmethod
    async def _execute_load_rule(load_rule, event_data: dict) -> list:
        execute = load_rule(event_data).execute

        if iscoroutinefunction(load_rule):
            return await execute()

        else:
            return execute()

    async def _delete_events_from_storage(self, keys: list[str], event_type: str) -> None:
        await self.redis_storage.delete_(names=keys)

        logger.debug(f"{event_type}(keys={keys}) was delete from Storage")
