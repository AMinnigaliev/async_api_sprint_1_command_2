import socket
from datetime import datetime

from sqlalchemy import select

from core import config
from models.movies.pg_models import Person
from interface import DataBaseUOW_T
from schemas.movies_schemas.person_models import PersonModel
from utils import backoff_by_connection


class PersonRules:

    @classmethod
    @backoff_by_connection(exceptions=(ConnectionRefusedError, socket.gaierror))
    async def person_selection_data_rule(
        cls,
        db_uow: DataBaseUOW_T,
        date_modified: datetime,
    ) -> list[Person]:
        limit = config.etl_movies_select_limit

        query_ = await db_uow.scalars(
            select(Person)
            .where(Person.modified >= date_modified)
            .order_by(Person.modified)
            .limit(limit)
        )
        persons = query_.all()

        return persons

    @classmethod
    def person_normalize_data_rule(
        cls, selection_data: list[Person]
    ) -> list[PersonModel]:
        normalized_data = [
            PersonModel(
                id=person.id,
                full_name=person.full_name,
            )
            for person in selection_data
        ]

        return normalized_data
