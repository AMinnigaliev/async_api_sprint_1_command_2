import enum


class EventsEnum(enum.Enum):
    CLICK = "element_click"
    VIEW_PAGE = "событие: Просмотр страницы"
    CHANGE_VIDEO_QUALITY = "событие: Смена качества видео"
    WATCH_VIDEO_TO_END = "событие: Просмотр видео до конца"
    USING_SEARCH_FILTERS = "событие: Использование фильтров поиска"
