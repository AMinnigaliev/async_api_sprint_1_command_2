from flask import Blueprint, request
from datetime import datetime

from ..core.auth_client import get_user_id
from ..core.kafka_client import publish_event
from ..core.config import KAFKA_TOPIC
from ..models.event import EventSchema

bp = Blueprint("events", __name__, url_prefix="/events")


@bp.route("", methods=["POST"])
def receive_event():
    """
    Принимает одно JSON‑событие и публикует его в Kafka.
    (Расширение для bulk‑NDJSON можно добавить позже.)
    """
    # 1. Валидация payload
    schema = EventSchema.parse_obj(request.json)
    event_obj = schema.root  # TODO: schema.__root__ - устаревшее

    # 2. Обогащаем user_id
    token = event_obj.token
    user_id = get_user_id(token) if token else "anonymous"

    # 3. Формируем финальный JSON
    msg = event_obj.dict()
    msg.pop("token", None)                    # убираем токен
    msg["user_id"] = user_id                  # добавляем uid
    msg["timestamp"] = datetime.utcnow().isoformat()

    # 4. Отправляем в Kafka (ключ = название события)
    publish_event(KAFKA_TOPIC, key=msg["event"], event=msg)

    return "", 204
