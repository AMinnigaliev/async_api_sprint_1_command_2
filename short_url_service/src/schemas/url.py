from pydantic import BaseModel, Field, HttpUrl


class FullUrl(BaseModel):
    """Модель для полной ссылки."""
    url: HttpUrl = Field(..., description="Полная ссылка")


class ShortUrl(BaseModel):
    """Модель для сокращённой ссылки."""
    short_url: HttpUrl = Field(..., description="Сокращённая ссылка")
