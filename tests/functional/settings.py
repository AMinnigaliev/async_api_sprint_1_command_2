from uuid import uuid4

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from testdata.es_mapping import ESIndexMapping, get_es_index_mapping, get_persons_index_mapping


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    skip_test: str = Field(default="true", alias="SKIP_TEST")

    src_app_host: str = Field(default="127.0.0.1", alias="SRC_APP_HOST")
    src_app_port: int = Field(default=8000, alias="SRC_APP_PORT")

    redis_host: str = Field(default="127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    elastic_schema: str = Field(default="film", alias="ELASTIC_SCHEMA")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_host: str = Field(default="127.0.0.1", alias="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, alias="ELASTIC_PORT")
    elastic_password: str = Field(default="123qwe", alias="ES_PASSWORD")

    elastic_index: str = "films"  # TODO: bad
    elastic_id_field: str = Field(default_factory=lambda: str(uuid4()))
    elastic_index_mapping: ESIndexMapping = get_es_index_mapping()
    elastic_persons_index_mapping: ESIndexMapping = get_persons_index_mapping()

    postgres_driver_name: str = Field(
        default="postgresql+psycopg2", alias="POSTGRES_DRIVER_NAME"
    )
    postgres_db: str = Field(default="name", alias="PG_NAME")
    postgres_user: str = Field(default="user", alias="PG_USER")
    postgres_host: str = Field(default="127.0.0.1", alias="PG_HOST")
    postgres_port: int = Field(default=5432, alias="PG_PORT")
    postgres_password: str = Field(default="password", alias="PG_PASSWORD")

    request_timeout: int = Field(default=1 * 30, alias="REQUEST_TIME_OUT")
    max_connection_attempt: int = Field(default=5, alias="MAX_CONNECTION_ATTEMPT")
    break_time_sec: int = Field(default=5, alias="BREAK_TIME_SEC")

    @computed_field
    @property
    def service_url(self) -> str:
        return f"http://{self.src_app_host}:{self.src_app_port}"


config = TestSettings()
