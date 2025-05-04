from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core import config
from interface import redis_context_manager, db_uow_, es_context_manager
from extract.producer import Producer
from extract.enricher import Enricher
from transfer import Convertor
from loader.loader import Loader


class MoviesETLScheduler:

    @classmethod
    def jobs_(cls) -> list[dict]:
        return [
            {
                "cls_job": Producer,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": Enricher,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": Convertor,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
            {
                "cls_job": Loader,
                "job_params": {
                    "trigger": config.etl_task_trigger,
                    "seconds": config.etl_task_interval_sec,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
        ]

    @classmethod
    async def run(cls) -> None:
        async with redis_context_manager as redis_storage, db_uow_ as db_uow, es_context_manager as es_client:
            scheduler_ = AsyncIOScheduler()

            for job_ in cls.jobs_():
                scheduler_.add_job(
                    func=job_["cls_job"](redis_storage, db_uow, es_client).run,
                    **job_["job_params"]
                )

            scheduler_.start()
