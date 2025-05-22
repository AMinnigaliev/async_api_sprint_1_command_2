import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()


class Models(Enum):
    """Наименование моделей данных"""

    users = "Пользователи"
    film_works = "Фильмы"
    user_film_markers = "Закладки фильмов пользователей"
    user_rating_films = "Оценка фильмов пользователями"
    user_review_films = "Рецензия фильма пользователем"
    user_rating_reviews = "Оценка рецензии пользователем"

    @classmethod
    def pg_create(cls) -> dict[str, list[str, str | dict[str, str]]]:
        return {
            cls.users.name: [
                "id UUID PRIMARY KEY",
                "name TEXT NOT NULL",
                {
                    "shard_key": os.getenv("USERS_SHARD_KEY", "id"),
                },
            ],
            cls.film_works.name: [
                "id UUID PRIMARY KEY",
                "title TEXT NOT NULL",
                "description TEXT",
                "creation_date TIMESTAMP",
                "rating DOUBLE PRECISION",
                "type TEXT NOT NULL",
                "created TIMESTAMP",
                "modified TIMESTAMP",
                {
                    "shard_key": os.getenv("FILM_WORKS_SHARD_KEY", "id"),
                },
            ],
            cls.user_film_markers.name: [
                "id UUID PRIMARY KEY",
                "user_id UUID",
                "film_id UUID",
                "timestamp TIMESTAMP",
                {
                    'column': 'user_id',
                    'references': {
                        'table': cls.users.name,
                        'column': 'id'
                    },
                },
                {
                    'column': 'film_id',
                    'references': {
                        'table': cls.film_works.name,
                        'column': 'id'
                    },
                },
                {
                    "shard_key": os.getenv("USER_FILM_MARKERS_SHARD_KEY", "user_id"),
                    "indexes": [os.getenv("USER_RATING_REVIEWS_INDEX_KEY", "user_id"), ]
                },
            ],
            cls.user_rating_films.name: [
                "id UUID PRIMARY KEY",
                "user_id UUID",
                "film_id UUID",
                "rating INTEGER",
                "timestamp TIMESTAMP",
                {
                    'column': 'user_id',
                    'references': {
                        'table': cls.users.name,
                        'column': 'id'
                    },
                },
                {
                    'column': 'film_id',
                    'references': {
                        'table': cls.film_works.name,
                        'column': 'id'
                    },
                },
                {
                    "shard_key": os.getenv("USER_RATING_FILMS_SHARD_KEY", "film_id"),
                    "indexes": [os.getenv("USER_RATING_REVIEWS_INDEX_KEY", "film_id"), ]
                },
            ],
            cls.user_review_films.name: [
                "id UUID PRIMARY KEY",
                "user_id UUID",
                "film_id UUID",
                "user_rating_id UUID",
                "timestamp TIMESTAMP",
                {
                    'column': 'user_id',
                    'references': {
                        'table': cls.users.name,
                        'column': 'id'
                    },
                },
                {
                    'column': 'film_id',
                    'references': {
                        'table': cls.film_works.name,
                        'column': 'id'
                    },
                },
                {
                    "shard_key": os.getenv("USER_REVIEW_FILMS_SHARD_KEY", "film_id"),
                    "indexes": [os.getenv("USER_RATING_REVIEWS_INDEX_KEY", "film_id"), ]
                },
            ],
            cls.user_rating_reviews.name: [
                "id UUID PRIMARY KEY",
                "user_id UUID",
                "user_review_id UUID",
                "rating BOOLEAN",
                "timestamp TIMESTAMP",
                {
                    'column': 'user_id',
                    'references': {
                        'table': cls.users.name,
                        'column': 'id'
                    },
                },
                {
                    'column': 'user_review_id',
                    'references': {
                        'table': cls.user_review_films.name,
                        'column': 'id'
                    },
                },
                {
                    "shard_key": os.getenv("USER_RATING_REVIEWS_SHARD_KEY", "user_id"),
                    "indexes": [os.getenv("USER_RATING_REVIEWS_INDEX_KEY", "user_id"), ]
                },
            ]
        }
