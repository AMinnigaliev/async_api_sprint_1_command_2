import time

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError

from logger import logger
from settings import config


if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=[
            f"{config.elastic_schema}://{config.elastic_host}:"
            f"{config.elastic_port}"
        ],
        basic_auth=(config.elastic_name, config.elastic_password),
    )
    concat_ = 1
    connection_attempt = 0

    while connection_attempt <= config.max_connection_attempt:
        try:
            if es_client.ping():
                es_client.close()
                logger.debug("Connection to Elasticsearch has been made")

                break

            time.sleep(config.break_time_sec)
            connection_attempt += concat_

            if connection_attempt == config.max_connection_attempt:
                raise ConnectionError("number of connection attempts exceeded")

        except (ElasticsearchConnectionError, ConnectionError) as ex:
            logger.error(f"Elasticsearch is not yet available. Error: {ex}")
            raise
