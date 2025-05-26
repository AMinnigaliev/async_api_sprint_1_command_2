import json
from asyncio import iscoroutinefunction
from typing import Callable

from core.logger import logger
from extract.events.producer_rules import (ElementClickEventRule,
                                           PageViewEventRule,
                                           QualityChangeEventRule,
                                           SearchFilterEventRule,
                                           VideoCompleteEventRule)
from interface import KafkaConsumerUOW, RedisStorage_T
from models.events import EventsEnum


class Producer:
    """Класс по получению данных из Kafka."""

    def __init__(self, clickhouse_session_, redis_storage: RedisStorage_T):
        self._redis_storage: RedisStorage_T = redis_storage
        self._clickhouse_session = clickhouse_session_
        self._kafka_consumer_uow: KafkaConsumerUOW | None = None

    @property
    def clickhouse_session(self):
        return self._clickhouse_session

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
            EventsEnum.ELEMENT_CLICK.value: ElementClickEventRule,
            EventsEnum.PAGE_VIEW.value: PageViewEventRule,
            EventsEnum.QUALITY_CHANGE.value: QualityChangeEventRule,
            EventsEnum.VIDEO_COMPLETE.value: VideoCompleteEventRule,
            EventsEnum.SEARCH_FILTER.value: SearchFilterEventRule,
        }

    async def run(self) -> None:
        """
        Точка запуска. Этапы:
        - Получение сообщений из Kafka.
        - Выполнение правила по обработке события (в случае его наличия).
        - Отправка в Storage обработанного события для обработки Loader-ом.

        :return None:
        """
        for event_message in (
            self.kafka_consumer_uow.gen_pool_messages_from_topics()
        ):
            event_key = self.kafka_consumer_uow.get_message_key(
                event_message=event_message
            )

            if event_rule := self.events_rules.get(event_key):
                event_storage_key, event_data = await self._execute_event_rule(
                    event_rule=event_rule,
                    event_key=event_key,
                    event_value=self.kafka_consumer_uow.get_message_value(
                        event_message=event_message
                    ),
                )

                if event_storage_key and event_data:
                    await self._insert_event_data_in_storage(
                        event_storage_key=event_storage_key,
                        event_data=event_data,
                    )
                    logger.info(
                        f"Event '{event_key}'(EventStorageKey="
                        f"{event_storage_key}) was Produce"
                    )

    @staticmethod
    async def _execute_event_rule(
            event_rule: Callable, event_key: str, event_value: dict
    ) -> tuple:
        execute_method = event_rule(event_value, event_key).execute

        if iscoroutinefunction(execute_method):
            event_storage_key, event_data = await execute_method()

        else:
            event_storage_key, event_data = execute_method()

        return event_storage_key, event_data

    async def _insert_event_data_in_storage(
            self, event_storage_key: str, event_data: dict | str
    ) -> None:
        value = event_data if isinstance(event_data, str) else json.dumps(
            event_data
        )
        await self.redis_storage.save_state(
            key_=event_storage_key, value=value
        )

        logger.debug(
            f"EventStorageKey={event_storage_key} was was insert in Storage"
        )
