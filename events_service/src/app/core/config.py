import os

# -------------------- auth service -------------------- #
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")

# кеш токена (сек.)
TOKEN_CACHE_TTL = int(os.getenv("TOKEN_CACHE_TTL", "300"))

# ---------------------- Redis ------------------------- #
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# ---------------------- Kafka ------------------------- #
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
KAFKA_TOPIC   = os.getenv("KAFKA_TOPIC",   "events")  # один топик
