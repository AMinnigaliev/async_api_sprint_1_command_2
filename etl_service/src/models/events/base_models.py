from pydantic import BaseModel


class QualityChangeDC(BaseModel):
    user_id: str
    timestamp: str

    video_id: str
    old_quality: int
    new_quality: int


class VideoCompleteDC(BaseModel):
    user_id: str
    timestamp: str

    video_id: str
    duration_total: bool


class SearchFilterDC(BaseModel):
    user_id: str
    timestamp: str

    search_query: str
    filters: str


class PageViewDC(BaseModel):
    user_id: str
    timestamp: str

    element_page_type: str
    page_number: int
