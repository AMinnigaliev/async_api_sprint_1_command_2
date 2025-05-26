from infi.clickhouse_orm import Model, fields
from infi.clickhouse_orm.engines import MergeTree


class ClickElementEventModel(Model):
    __table__ = 'click_element'

    user_id = fields.StringField()
    page_type = fields.StringField()
    element_type = fields.StringField()
    timestamp = fields.DateTimeField()

    engine = MergeTree('timestamp', ('user_id',))


class QualityChangeEventModel(Model):
    __table__ = 'quality_change'

    user_id = fields.StringField()
    timestamp = fields.DateTimeField()

    video_id = fields.StringField()
    old_quality = fields.Int16Field()
    new_quality = fields.Int16Field()

    engine = MergeTree('timestamp', ('user_id',))


class VideoCompleteEventModel(Model):
    __table__ = 'video_complete'

    user_id = fields.StringField()
    timestamp = fields.DateTimeField()

    video_id = fields.StringField()
    duration_total = fields.Int8Field()

    engine = MergeTree('timestamp', ('user_id',))


class SearchFilterEventModel(Model):
    __table__ = 'search_filter'

    user_id = fields.StringField()
    timestamp = fields.DateTimeField()

    search_query = fields.StringField()
    filters = fields.StringField()

    engine = MergeTree('timestamp', ('user_id',))


class PageViewModel(Model):
    __table__ = 'page_view'

    user_id = fields.StringField()
    timestamp = fields.DateTimeField()

    element_page_type = fields.StringField()
    page_number = fields.StringField()

    engine = MergeTree('timestamp', ('user_id',))
