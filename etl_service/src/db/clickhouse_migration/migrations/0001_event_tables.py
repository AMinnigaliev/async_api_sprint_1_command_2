from models.events.clickhouse_models import (
    ClickElementEventModel,
    QualityChangeEventModel,
    VideoCompleteEventModel,
    SearchFilterEventModel,
    PageViewModel,
)


def migrate(session):
    models = [
        ClickElementEventModel,
        QualityChangeEventModel,
        VideoCompleteEventModel,
        SearchFilterEventModel,
        PageViewModel,
    ]

    for model in models:
        if not session.does_table_exist(model):
            session.create_table(model)
