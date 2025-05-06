from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core import config
from utils.abstract import ETLSchedulerInterface
from interface import redis_context_manager, postgres_uow_, clickhouse_uow_, es_context_manager

from extract.movies.producer import Producer as MoviesProducer
from extract.movies.enricher import Enricher as MoviesEnricher
from transfer.movies.convertor import Convertor as MoviesConvertor
from loader.movies_loader import Loader as MoviesLoader

from extract.events.producer import Producer as EventsProducer  # TODO:
# from extract.events.enricher import Enricher as EventsEnricher  # TODO:
# from transfer.events.convertor import Convertor as EventsConvertor  # TODO:
# from loader.events import Loader as EventsLoader  # TODO:


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

        async with redis_context_manager as redis_storage, postgres_uow_ as db_uow, es_context_manager as es_client:
            for job_ in cls.jobs():
                scheduler_.add_job(
                    func=job_["cls_job"](redis_storage, db_uow, es_client).run,
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
                    "seconds": config.etl_event_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            # {
            #     "cls_job": EventsEnricher,
            #     "job_params": {
            #         "trigger": config.etl_task_trigger,
            #         "seconds": config.etl_event_task_interval_sec,
            #         "coalesce": True,
            #         "max_instances": 1,
            #         "misfire_grace_time": None,
            #     },
            # },
            # {
            #     "cls_job": EventsConvertor,
            #     "job_params": {
            #         "trigger": config.etl_task_trigger,
            #         "seconds": config.etl_event_task_interval_sec,
            #         "coalesce": True,
            #         "max_instances": 1,
            #         "misfire_grace_time": None,
            #     },
            # },
            # {
            #     "cls_job": EventsLoader,
            #     "job_params": {
            #         "trigger": config.etl_task_trigger,
            #         "seconds": config.etl_event_task_interval_sec,
            #         "coalesce": True,
            #         "max_instances": 1,
            #         "misfire_grace_time": None,
            #     },
            # },
        ]

    @classmethod
    async def run(cls) -> None:
        scheduler_ = AsyncIOScheduler()

        with clickhouse_uow_ as clickhouse_uow:
            async with redis_context_manager as redis_storage:
                for job_ in cls.jobs():
                    scheduler_.add_job(func=job_["cls_job"](clickhouse_uow, redis_storage).run, **job_["job_params"])

                scheduler_.start()
