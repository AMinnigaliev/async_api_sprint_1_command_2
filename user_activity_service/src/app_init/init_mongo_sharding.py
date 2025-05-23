#!/usr/bin/env python3
"""
Скрипт инициализации шардированного кластера MongoDB на Python.
Выполняет rs.initiate, добавляет шарды, включает шардирование базы
и шардирует коллекции.
"""
import os
import time
import logging.config
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from src.core.logger import LOGGING

# Настраиваем логирование
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

# Чтение параметров из окружения или настроек
MONGO_NAME = os.getenv('MONGO_NAME')
CONFIG_RS = 'mongors1conf'
SHARD1_RS = 'mongors1'
SHARD2_RS = 'mongors2'

# Адреса нод в Docker-сети
CONFIG_NODES = ['mongocfg1:27017', 'mongocfg2:27017', 'mongocfg3:27017']
SHARD1_NODES = ['mongors1n1:27017', 'mongors1n2:27017', 'mongors1n3:27017']
SHARD2_NODES = ['mongors2n1:27017', 'mongors2n2:27017', 'mongors2n3:27017']


def build_uri(hosts):
    """Формирует строку подключения к MongoDB."""
    hosts_str = ','.join(hosts)
    uri = f"mongodb://{hosts_str}/admin"

    logger.debug("Сформирован URI: %s", uri)

    return uri


def wait_for(hosts, desc):
    """Ожидает доступности MongoDB на заданных узлах."""
    uri = build_uri(hosts)
    logger.info("Ожидание доступности %s по адресам: %s", desc, hosts)
    while True:
        client = None
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            logger.info("%s доступен.", desc)
            return client

        except ServerSelectionTimeoutError:
            logger.warning("%s недоступен, пробуем снова...", desc)
            time.sleep(2)

        finally:
            if client:
                client.close()


def initiate_rs(client, rs_name, members, configsvr=False):
    """Инициализирует replica set."""
    cfg = {
        '_id': rs_name,
        'members': [{'_id': i, 'host': host} for i, host in enumerate(members)]
    }
    if configsvr:
        cfg['configsvr'] = True

    try:
        logger.info("Инициализация реплика-сета '%s'...", rs_name)
        client.admin.command('replSetInitiate', cfg)
        logger.info("Реплика-сет '%s' успешно инициализирован.", rs_name)

    except OperationFailure as e:
        if 'already initiated' in str(e) or 'already initialized' in str(e):
            logger.info(
              "Реплика-сет '%s' уже инициализирован.", rs_name)

        else:
            logger.error(
              "Ошибка инициализации реплика-сета '%s': %s", rs_name, e
            )
            raise


def add_shards(mongos_client):
    """Добавляет шардовые replica set в кластер через mongos."""
    try:
        logger.info("Добавление шардов в кластер через mongos...")

        mongos_client.admin.command(
          'addShard', f"{SHARD1_RS}/{','.join(SHARD1_NODES)}"
        )
        mongos_client.admin.command(
          'addShard', f"{SHARD2_RS}/{','.join(SHARD2_NODES)}"
        )
        logger.info("Шарды успешно добавлены в кластер.")

    except Exception as e:
        logger.error("Ошибка при добавлении шардов: %s", e)
        raise


def shard_collections(mongos_client):
    """Включает шардирование базы и распределяет коллекции по ключам."""
    try:
        logger.info("Включение шардирования базы '%s'...", MONGO_NAME)

        mongos_client.admin.command('enableSharding', MONGO_NAME)
        shards = {
            'film_ratings': 'film_id',
            'film_reviews': 'film_id',
            'review_ratings': 'review_id',
            'bookmarks': 'user_id',
            'overall_film_ratings': 'film_id',
            'overall_review_ratings': 'review_id'
        }
        for coll, key in shards.items():
            namespace = f"{MONGO_NAME}.{coll}"
            logger.info(
              "Шардирование коллекции '%s' по ключу '%s' (hashed)...",
              namespace, key
            )
            mongos_client.admin.command(
              'shardCollection', namespace, key={key: 'hashed'}
            )

        logger.info("Все коллекции зашардированы.")

    except Exception as e:
        logger.error("Ошибка при шардировании коллекций: %s", e)
        raise


if __name__ == '__main__':
    try:
        cfg_client = wait_for(CONFIG_NODES, 'конфиг-серверов')
        initiate_rs(cfg_client, CONFIG_RS, CONFIG_NODES, configsvr=True)

        s1_client = wait_for(SHARD1_NODES, 'шард-нод shard1')
        initiate_rs(s1_client, SHARD1_RS, SHARD1_NODES)
        s2_client = wait_for(SHARD2_NODES, 'шард-нод shard2')
        initiate_rs(s2_client, SHARD2_RS, SHARD2_NODES)

        mongos_client = wait_for(['mongos1:27017'], 'mongos1 (router)')

        add_shards(mongos_client)
        shard_collections(mongos_client)

        logger.info("Инициализация кластера MongoDB завершена успешно.")

    finally:
        for client in (cfg_client, s1_client, s2_client, mongos_client):
            try:
                client.close()
                logger.debug("Соединение закрыто.")

            except Exception as e:
                logger.error("Ошибка при закрытии клиента MongoDB: %s", e)
                pass
