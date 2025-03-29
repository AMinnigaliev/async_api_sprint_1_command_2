import time

import redis
from redis.exceptions import ConnectionError as RedisConnectionError

from logger import logger
from settings import config


if __name__ == '__main__':
    redis_client = redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_password,
        db=config.redis_db,
    )
    concat_ = 1
    connection_attempt = 0

    while connection_attempt <= config.max_connection_attempt:
        try:
            if redis_client.ping():
                redis_client.close()
                logger.debug("Connection to Redis has been made")

                break

            time.sleep(config.break_time_sec)
            connection_attempt += concat_

            if connection_attempt == config.max_connection_attempt:
                raise ConnectionError("number of connection attempts exceeded")

        except (RedisConnectionError, ConnectionError) as ex:
            logger.error(f"Redis is not yet available. Error: {ex}")
            raise
