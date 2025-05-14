import json
import time
from contextlib import contextmanager
from typing import Any, Generator

from confluent_kafka import Consumer, Message

from core import config
from core.logger import logger


class KafkaConsumerUOW:
    MAX_STEP = 0.5
    START_STEP = 0
    CONCAT = 0.1

    def __init__(self) -> None:
        self.__consumer: Consumer | None = None

    @property
    def conf(self) -> dict:
        return {
            "bootstrap.servers": config.kafka_broker,
            "group.id": config.kafka_consumer_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": config.kafka_enable_auto_commit,
        }

    @property
    def topics(self) -> list:
        return [config.kafka_events_topic, ]

    @staticmethod
    def get_message_key(event_message: Message) -> str:
        return event_message.key().decode("utf-8")

    @staticmethod
    def get_message_value(event_message: Message) -> dict:
        return json.loads(event_message.value().decode("utf-8"))

    @contextmanager
    def consumer(self) -> Generator[Consumer, Any, None]:
        if not self.__consumer:
            self.__consumer = Consumer(self.conf)
            self.__consumer.subscribe(self.topics)

        try:
            yield self.__consumer

        except Exception as ex:
            logger.error(f"KafkaUOW error: {ex}")
            raise

        finally:
            try:
                self.__consumer.close()

            except Exception as close_ex:
                logger.error(f"Error close Kafka consumer: {close_ex}")

            self.__consumer = None

    def gen_pool_messages_from_topics(self):
        with self.consumer() as consumer:
            step = self.START_STEP

            while self.MAX_STEP > step:
                if pool_messages := consumer.consume(config.etl_events_select_limit, config.kafka_consumer_timeout):
                    for pool_message in pool_messages:
                        yield pool_message

                    consumer.commit()
                    break

                else:
                    step += self.CONCAT
                    time.sleep(step)
