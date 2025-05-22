from tests.database_comparison.pg_uow import PGUOW
from tests.database_comparison.mongo_uow import MongoUOW
from tests.database_comparison.custom_enum import Models
from tests.database_comparison.logger import logger


def user_like_rating_films_by_user(pg_uow: PGUOW, mongo_uow: MongoUOW, user_id: str, min_: int = 7):
    user_rating_films_from_pg, select_time_pg = pg_uow.select_data(
        table_name=Models.user_rating_films.name,
        filters_={
            "user_id": {
                "operator": "=",
                "value": f"'{user_id}'",
            },
            "rating": {
                "operator": ">=",
                "value": f"{min_}",
            }
        },
    )
    user_rating_films_from_mongo, select_time_mongo = mongo_uow.select_data(
        collection_name=Models.user_rating_films.name,
        filters_={
            "user_id": user_id,
            "rating": {"$gte": min_}
        },
    )

    select_pg_len = len(user_rating_films_from_pg)
    select_mongo_len = len(user_rating_films_from_mongo)
    if select_pg_len != select_mongo_len:
        logger.warning(
            f"Case_1(user_like_rating_films_by_user): количество select-данных не совпадает: "
            f"PG({select_pg_len}), Mongo({select_mongo_len})"
        )

    if select_time_pg < select_time_mongo:
        logger.info(
            f"Case_1(user_like_rating_films_by_user): "
            f"select-запрос в PG({select_time_pg}; {select_pg_len}) выполнился быстрее, "
            f"чем в Mongo({select_time_mongo}; {select_mongo_len})"
        )

    elif select_time_pg > select_time_mongo:
        logger.info(
            f"Case_1(user_like_rating_films_by_user): "
            f"select-запрос в Mongo({select_time_mongo}; {select_mongo_len}) "
            f"выполнился быстрее, чем в PG({select_time_pg}; {select_pg_len})"
        )

    else:
        logger.info(
            f"Case_1(user_like_rating_films_by_user): "
            f"select-запрос в PG({select_time_pg}; {select_pg_len}) и Mongo({select_time_mongo}; {select_mongo_len}) "
            f"выполнился с одинаковой скоростью"
        )
