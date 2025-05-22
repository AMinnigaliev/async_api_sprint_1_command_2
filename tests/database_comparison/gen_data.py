import uuid
from random import randint
from typing import Any
from datetime import datetime
from collections import defaultdict

from tests.database_comparison.custom_enum import Models


class GenData:

    def __init__(self, count_entities: int) -> None:
        self._count_entities = count_entities
        self._init_data = defaultdict(list)

    def _gen_users_data(self, min_: int = 1, max_ = 11, delimiter: int = 1_000) -> list[dict[str, str]]:
        return [
            {"id": str(uuid.uuid4()), "name": f"user_{randint(min_, max_)}"}
            for _ in range(self._count_entities // delimiter)
        ]

    def _gen_film_works_data(self, min_: int = 1, max_=11, delimiter: int = 1_000) -> list[dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4()),
                "title": f"title_{randint(min_, max_)}",
                "description": f"description_{randint(min_, max_)}",
                "creation_date": datetime.today(),
                "rating": randint(min_, max_),
                "type": f"type_{randint(min_, max_)}",
                "created": datetime.today(),
                "modified": datetime.today(),
            } for _ in range(self._count_entities // delimiter)
        ]

    def _gen_user_film_markers_data(self, min_: int = 1, delimiter: int = 1_000) -> list[dict[str, Any]]:
        user_film_markers_ = list()

        for _ in range(self._count_entities):
            user_id = (
                self._init_data[Models.users.name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )
            film_id = (
                self._init_data[Models.film_works.name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )

            user_film_markers_.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "film_id": film_id,
                    "timestamp": datetime.today(),
                }
            )

        return user_film_markers_

    def _gen_user_rating_films_data(self, min_: int = 1, max_: int = 11, delimiter: int = 1_000) -> list[dict[str, Any]]:
        user_rating_films_ = list()

        for _ in range(self._count_entities):
            user_id = (
                self._init_data[Models.users.name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )
            film_id = (
                self._init_data[Models.film_works.name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )

            user_rating_films_.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "film_id": film_id,
                    "rating": randint(min_, max_),
                    "timestamp": datetime.today(),
                }
            )

        return user_rating_films_

    def _gen_user_review_films_data(self, min_: int = 1, delimiter: int = 1_000) -> list[dict[str, Any]]:
        user_review_films_ = list()

        for index in range(self._count_entities):
            user_id = (
                self._init_data[Models.users.name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )
            film_id = (
                self._init_data[Models.film_works.name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )

            user_review_films_.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "film_id": film_id,
                    "user_rating_id": self._init_data[Models.user_rating_films.name][index]["id"],
                    "timestamp": datetime.today(),
                }
            )

        return user_review_films_

    def _gen_user_rating_reviews_data(self, min_: int = 1, delimiter: int = 1_000) -> list[dict[str, Any]]:
        user_rating_reviews_ = list()

        for index in range(self._count_entities):
            user_id = (
                self._init_data[Models.users.name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )
            user_review_films_name = Models.user_review_films.name
            user_review_film_id = (
                self._init_data[user_review_films_name][randint(min_, self._count_entities // delimiter - min_)]["id"]
            )

            user_rating_reviews_.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "user_review_id": user_review_film_id,
                    "rating": bool(randint(0, 2)),
                    "timestamp": datetime.today(),
                }
            )

        return user_rating_reviews_

    def run(self) -> dict[str, Any]:
        self._init_data[Models.users.name].extend(self._gen_users_data())
        self._init_data[Models.film_works.name].extend(self._gen_film_works_data())
        self._init_data[Models.user_film_markers.name] = self._gen_user_film_markers_data()
        self._init_data[Models.user_rating_films.name] = self._gen_user_rating_films_data()
        self._init_data[Models.user_review_films.name] = self._gen_user_review_films_data()
        self._init_data[Models.user_rating_reviews.name] = self._gen_user_rating_reviews_data()

        return self._init_data
