from pydantic import BaseModel


class ClickElementDC(BaseModel):
    data: dict

    user_id: str
    element_type: str | None = None
    timestamp: str | None = None


class ClickElementPlayMovies(BaseModel):
    user_id: str
    page_type: str

    element_type: str | None = None
    timestamp: str | None = None
