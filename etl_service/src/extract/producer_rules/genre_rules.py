import socket
from datetime import datetime

from sqlalchemy import select

from core import config
from models.movies_models.pg_models import Genre
from interface import DataBaseUOW_T
from schemas.movies_schemas.genre_models import GenreModel
from utils import backoff_by_connection


class GenreRules:

    @classmethod
    @backoff_by_connection(exceptions=(ConnectionRefusedError, socket.gaierror))
    async def genre_selection_data_rule(
        cls, db_uow: DataBaseUOW_T, date_modified: datetime
    ) -> list[Genre]:
        limit = config.etl_select_limit

        query_ = await db_uow.scalars(
            select(Genre)
            .where(Genre.modified >= date_modified)
            .order_by(Genre.modified)
            .limit(limit)
        )
        genres = query_.all()

        return genres

    @classmethod
    def genre_normalize_data_rule(cls, selection_data: list[Genre]) -> list[GenreModel]:
        normalized_data = [
            GenreModel(
                id=genre.id,
                name=genre.name,
                description=genre.description if genre.description else "",
            )
            for genre in selection_data
        ]

        return normalized_data
