from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core import config
from db.clickhouse_session import clickhouse_session
from db.postgres_session import pg_scoped_session
from extract.events.producer import Producer as EventsProducer
from extract.movies.enricher import Enricher as MoviesEnricher
from extract.movies.producer import Producer as MoviesProducer
from interface import RedisContextManager, es_context_manager
from loader.events_loader import Loader as EventsLoader
from loader.movies_loader import Loader as MoviesLoader
from transfer.movies.convertor import Convertor as MoviesConvertor
from utils.abstract import ETLSchedulerInterface


class MoviesETLScheduler(ETLSchedulerInterface):
    """Планировщик ETL-событий для сервиса 'Movies' (movies_service)."""

    @classmethod
    def jobs(cls) -> list[dict]:
        return [
            {
                "cls_job": MoviesProducer,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_movies_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": MoviesEnricher,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_movies_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": MoviesConvertor,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_movies_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": MoviesLoader,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_movies_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
        ]

    @classmethod
    async def run(cls) -> None:
        scheduler_ = AsyncIOScheduler()

        async with (
            RedisContextManager(
                redis_db=config.redis_db_movies
            ) as redis_storage,
            pg_scoped_session.context_session() as pg_session,
            es_context_manager as es_client,
        ):
            for job_ in cls.jobs():
                scheduler_.add_job(
                    func=job_["cls_job"](
                        redis_storage, pg_session, es_client
                    ).run,
                    **job_["job_params"]
                )

            scheduler_.start()


class EventsETLScheduler(ETLSchedulerInterface):
    """Планировщик ETL-событий для сервиса 'Events' (events_service)."""

    @classmethod
    def jobs(cls) -> list[dict]:
        return [
            {
                "cls_job": EventsProducer,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_events_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": EventsLoader,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_events_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
        ]

    @classmethod
    async def run(cls) -> None:
        scheduler_ = AsyncIOScheduler()

        with clickhouse_session.context_session() as clickhouse_session_:
            async with RedisContextManager(
                    redis_db=config.redis_db_events
            ) as redis_storage:
                for job_ in cls.jobs():
                    scheduler_.add_job(
                        func=job_["cls_job"](
                            clickhouse_session_, redis_storage
                        ).run,
                        **job_["job_params"],
                    )

                scheduler_.start()
