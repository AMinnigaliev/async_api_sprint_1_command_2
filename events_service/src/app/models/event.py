from pydantic import RootModel
from pydantic import BaseModel
from typing import Literal, Optional, Union

# ----------------- Data‑sub‑schemas ----------------- #

class ElementClickData(BaseModel):
    element_type: str
    page_type: str


class PageViewData(BaseModel):
    page_view_id: str
    page_type: str


class QualityChangeData(BaseModel):
    video_id: str
    old_quality: int
    new_quality: int


class VideoCompleteData(BaseModel):
    video_id: str
    duration_total: bool


class SearchFilterData(BaseModel):
    search_query: str
    filters: str


# ----------------- Event envelopes ----------------- #

class BaseEvent(BaseModel):
    """
    Общий конверт для всех входящих событий.
    Поле ``data`` валидируется в специализированных наследниках.
    """
    event: Literal[
        "element_click",
        "page_view_start",
        "page_view_end",
        "quality_change",
        "video_complete",
        "search_filter",
    ]
    token: Optional[str] = None
    data: dict


class ElementClickEvent(BaseEvent):
    event: Literal["element_click"]
    data: ElementClickData


class PageViewStartEvent(BaseEvent):
    event: Literal["page_view_start"]
    data: PageViewData


class PageViewEndEvent(BaseEvent):
    event: Literal["page_view_end"]
    data: PageViewData


class QualityChangeEvent(BaseEvent):
    event: Literal["quality_change"]
    data: QualityChangeData


class VideoCompleteEvent(BaseEvent):
    event: Literal["video_complete"]
    data: VideoCompleteData


class SearchFilterEvent(BaseEvent):
    event: Literal["search_filter"]
    data: SearchFilterData


# ----------------- Union‑schema for parsing ----------------- #

event_types = Union[
    ElementClickEvent,
    PageViewStartEvent,
    PageViewEndEvent,
    QualityChangeEvent,
    VideoCompleteEvent,
    SearchFilterEvent,
]


class EventSchema(RootModel[event_types]):
    """
    Главная Pydantic‑схема, которой валидируем *любой* входящий payload.
    """

    def to_dict(self) -> dict:
        """Удобный алиас для сериализации в dict."""
        return self.root.dict()
