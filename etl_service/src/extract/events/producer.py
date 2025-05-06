import json
from asyncio import iscoroutinefunction
from typing import Callable

from core.logger import logger
from models.events import EventsEnum
from interface import RedisStorage_T, check_free_size_storage, ClickhouseUOW_T, KafkaConsumerUOW


class Producer:
    """Класс по получению данных из Kafka."""

    def __init__(self, clickhouse_uow: ClickhouseUOW_T, redis_storage: RedisStorage_T):
        self._redis_storage: RedisStorage_T = redis_storage
        self._clickhouse_uow: ClickhouseUOW_T = clickhouse_uow
        self._kafka_consumer_uow: KafkaConsumerUOW | None = None

    @property
    def clickhouse_uow(self) -> ClickhouseUOW_T:
        return self._clickhouse_uow

    @property
    def redis_storage(self) -> RedisStorage_T:
        return self._redis_storage

    @property
    def kafka_consumer_uow(self) -> KafkaConsumerUOW:
        if not self._kafka_consumer_uow:
            self._kafka_consumer_uow = KafkaConsumerUOW()

        return self._kafka_consumer_uow

    @property
    def events_rules(self) -> dict:
        return {
            EventsEnum.CLICK.value: ClickEventRule,
            EventsEnum.VIEW_PAGE.value: ViewPageEventRule,
            EventsEnum.CHANGE_VIDEO_QUALITY.value: UsingSearchFiltersEventRule,
            EventsEnum.WATCH_VIDEO_TO_END.value: UsingSearchFiltersEventRule,
            EventsEnum.USING_SEARCH_FILTERS.value: UsingSearchFiltersEventRule,
        }

    async def run(self) -> None:
        """
        Точка запуска. Этапы:
        - Получение сообщений из Kafka.
        - Выполнение правила по обработке события (в случае его наличия).
        - Отправка в Storage обработанного события для обработки Loader-ом.

        :return None:
        """
        for event_message in self.kafka_consumer_uow.gen_pool_messages_from_topics():
            event_key = self.kafka_consumer_uow.get_message_key(event_message=event_message)

            if event_rule := self.events_rules.get(event_key):
                event_storage_key, event_data = await self._execute_event_rule(
                    event_rule=event_rule,
                    event_value=self.kafka_consumer_uow.get_message_value(event_message=event_message),
                )

                await self._insert_event_data_in_storage(event_storage_key=event_storage_key, event_data=event_data)

                logger.info(f"Event '{event_key}'(EventStorageKey={event_storage_key}) was Produce")

    @staticmethod
    async def _execute_event_rule(event_rule: Callable, event_value: dict) -> tuple:
        execute_method = event_rule(event_value).execute

        if iscoroutinefunction(execute_method):
            event_storage_key, event_data = await execute_method()

        else:
            event_storage_key, event_data = execute_method()

        return event_storage_key, event_data

    @check_free_size_storage()
    async def _insert_event_data_in_storage(self, event_storage_key: str, event_data: dict | str) -> None:
        value = event_data if isinstance(event_data, str) else json.dumps(event_data)
        await self.redis_storage.save_state(key_=event_storage_key, value=value)

        logger.debug(f"EventStorageKey={event_storage_key} was was insert in Storage")
