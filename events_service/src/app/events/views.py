import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from ..core.auth_client import get_user_id
from ..core.config import KAFKA_TOPIC
from ..core.kafka_client import publish_event
from ..models.event import EventSchema

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)

bp = Blueprint("events", __name__, url_prefix="/events")


@bp.route("", methods=["POST"])
def receive_event():
    """
    Принимает одно JSON-событие и публикует его в Kafka.
    (Расширение для bulk-NDJSON можно добавить позже.)
    """
    logger.debug("Incoming payload: %r", request.json)

    # 1. Валидация payload
    try:
        evt = EventSchema.parse_obj(request.json)
    except ValidationError as err:
        logger.warning("Invalid payload: %s", err.errors())
        return jsonify({"error": "Invalid payload"}), 400

    # 2. Обогащаем user_id
    token = evt.token
    user_id = get_user_id(token) if token else "anonymous"

    # 3. Формируем финальный JSON
    msg = evt.dict()
    msg.pop("token", None)                    # убираем токен
    msg["user_id"] = user_id                  # добавляем uid
    msg["timestamp"] = datetime.utcnow().isoformat()

    # 4. Отправляем в Kafka (ключ = название события)
    publish_event(KAFKA_TOPIC, key=msg["event"], event=msg)
    logger.info("Published event %s for user %s", msg["event"], user_id)

    return "", 204
