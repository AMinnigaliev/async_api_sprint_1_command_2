import enum


class EventsEnum(enum.Enum):
    ELEMENT_CLICK = "element_click"  # Клик
    PAGE_VIEW = "page_view"  # Просмотр страницы
    QUALITY_CHANGE = "quality_change"  # Смена качества видео
    VIDEO_COMPLETE = "video_complete"  # Просмотр видео до конца
    SEARCH_FILTER = "search_filter"  # Использование фильтров поиска
