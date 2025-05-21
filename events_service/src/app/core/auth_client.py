import requests
import jwt
from redis import Redis

from .config import AUTH_SERVICE_URL, TOKEN_CACHE_TTL, REDIS_URL

# --------------------------------------------------------------------------- #
# Redis‑кеш для валидации токенов
# --------------------------------------------------------------------------- #
db: Redis = Redis.from_url(REDIS_URL)


# --------------------------------------------------------------------------- #
# Утилиты
# --------------------------------------------------------------------------- #
def _decode_without_expiry(token: str) -> str:
    """
    Fallback‑декодирование JWT без проверки истечения срока.

    Возвращает user_id (claim *sub* или *user_id*) либо 'anonymous',
    если ни один из клеймов не найден.
    """
    claims = jwt.decode(
        token, options={"verify_exp": False}, algorithms=["HS256"]
    )
    return claims.get("sub") or claims.get("user_id") or "anonymous"


# --------------------------------------------------------------------------- #
# Основная функция
# --------------------------------------------------------------------------- #
def get_user_id(token: str) -> str:
    """
    Проверяет токен через auth‑service (с кешированием в Redis).
    Если сервис недоступен, декодирует JWT локально без проверки exp.

    :param token: строка JWT
    :return:     идентификатор пользователя или 'anonymous'
    """
    cache_key = f"token:{token}"
    cached = db.get(cache_key)
    if cached:
        return cached.decode()

    # --- онлайн‑валидация ---
    try:
        resp = requests.post(
            f"{AUTH_SERVICE_URL}/validate",
            json={"token": token},
            timeout=0.5,
        )
        resp.raise_for_status()
        user_id = resp.json().get("user_id", "anonymous")
    except Exception:
        # сервис не отвечает или вернул ошибку
        user_id = _decode_without_expiry(token)

    # записываем в кеш
    db.set(cache_key, user_id, ex=TOKEN_CACHE_TTL)
    return user_id
