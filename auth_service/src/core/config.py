import os
from typing import Any, ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings
from redis.exceptions import RedisError
from asyncpg.exceptions import PostgresError
from asyncpg.exceptions import SyntaxOrAccessError as PGSyntaxOrAccessError
from asyncpg.exceptions import ConnectionDoesNotExistError as PGConnectionDoesNotExistError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.exc import OperationalError as SQLOperationalError


class Settings(BaseSettings):
    project_name: str = Field(default="movies", env="PROJECT_NAME")
    base_dir: str = Field(
        default_factory=lambda: os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: str = Field("password", env="REDIS_PASSWORD")

    elastic_host: str = Field("elasticsearch", env="ELASTIC_HOST")
    elastic_port: int = Field(9200, env="ELASTIC_PORT")
    elastic_scheme: str = Field("http", env="ELASTIC_SCHEME")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_password: str = Field(default="123qwe", alias="ES_PASSWORD")

    pg_user: str = Field("user", env="PG_USER")
    pg_password: str = Field("password", env="PG_PASSWORD")
    pg_host: str = Field("postgres", env="PG_HOST")
    pg_port: int = Field(5432, env="PG_PORT")
    pg_name: str = Field("name", env="PG_NAME")

    # Exceptions
    redis_exceptions: Any = (RedisError,)
    pg_exceptions: Any = (
        PostgresError, PGConnectionDoesNotExistError, PGSyntaxOrAccessError
    )
    sql_exceptions: Any = (
        SQLAlchemyError, SQLIntegrityError, SQLOperationalError
    )

    # Безопасность
    token_revoke: ClassVar[bytes] = b"revoked"
    token_active: ClassVar[bytes] = b"active"
    secret_key: str = Field("practix", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    oauth: Dict[str, Dict[str, str]] = {
        "google": {
            "client_id": "your-google-client-id",
            "client_secret": "your-google-secret",
            "redirect_uri": "http://localhost:8000/auth/social/callback/google",
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo",
            "scope": "email profile"
        },
        "yandex": {
            "client_id": "your-yandex-client-id",
            "client_secret": "your-yandex-secret",
            "redirect_uri": "http://localhost:8000/auth/social/callback/yandex",
            "authorize_url": "https://oauth.yandex.ru/authorize",
            "token_url": "https://oauth.yandex.ru/token",
            "user_info_url": "https://login.yandex.ru/info",
            "scope": "login:email login:info"
        },
        "vk": {
            "client_id": "your-vk-client-id",
            "client_secret": "your-vk-secret",
            "redirect_uri": "http://localhost:8000/auth/social/callback/vk",
            "authorize_url": "https://oauth.vk.com/authorize",
            "token_url": "https://oauth.vk.com/access_token",
            "user_info_url": "https://api.vk.com/method/users.get?fields=uid,first_name,last_name,email&v=5.131",
            "scope": "email"
        },
    }

settings = Settings()
