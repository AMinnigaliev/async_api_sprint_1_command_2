"""Kafka helper: авто‑создаёт топик *events* при старте сервиса
и работает как неблокирующий продюсер, выдерживающий 600+ RPS.
"""
import json
import threading
import time

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic, KafkaException
from confluent_kafka import KafkaError

from .config import KAFKA_BROKERS, KAFKA_TOPIC

# --------------------------------------------------------------------------- #
# 1. Убеждаемся, что топик существует (создаёт один раз, без init‑контейнера)
# --------------------------------------------------------------------------- #


def _ensure_topic() -> None:
    admin = AdminClient({"bootstrap.servers": KAFKA_BROKERS})

    # Если уже есть — выходим
    metadata = admin.list_topics(timeout=5)
    if KAFKA_TOPIC in metadata.topics:
        return

    topic = NewTopic(
        topic=KAFKA_TOPIC,
        num_partitions=6,
        replication_factor=1,
        config={"compression.type": "lz4"},
    )
    futures = admin.create_topics([topic])

    try:
        futures[KAFKA_TOPIC].result(timeout=10)
        # поднимет исключение при ошибке
        print(f"[Kafka] topic '{KAFKA_TOPIC}' created (6 partitions, lz4)")
    except KafkaException as exc:
        if exc.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
            raise


_ensure_topic()

# --------------------------------------------------------------------------- #
# 2. Создаём idempotent Producer
# --------------------------------------------------------------------------- #


def _create_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": KAFKA_BROKERS,
            "enable.idempotence": True,
            "acks": "all",
            "compression.type": "lz4",
        }
    )


producer: Producer = _create_producer()

# --------------------------------------------------------------------------- #
# 3. Фоновый flush каждые 500 мс (чтобы не блокировать publish)
# --------------------------------------------------------------------------- #


def _flusher() -> None:
    while True:
        producer.flush(0.5)          # блокируемся максимум на 0.5 с
        time.sleep(0.5)


threading.Thread(target=_flusher, daemon=True).start()

# --------------------------------------------------------------------------- #
# 4. Публичная функция отправки
# --------------------------------------------------------------------------- #


def publish_event(topic: str, key: str, event: dict) -> None:
    """Fire‑and‑forget отправка без блокирующего flush."""
    payload = json.dumps(event).encode("utf-8")
    producer.produce(topic, key=key, value=payload)
    # poll(0) обслуживает внутренние колбэки, не задерживая поток запроса
    producer.poll(0)
