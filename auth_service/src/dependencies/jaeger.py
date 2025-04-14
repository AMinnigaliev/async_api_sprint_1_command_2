from fastapi import Request, status, HTTPException

from src.utils.jaeger_worker import JaegerWorker
from src.core.config import settings


def check_request_id(request: Request) -> None:
    """
    Проверка наличия 'X-Request-Id', установка в атрибут текущего span.

    @type request: Request
    @param request:

    @rtype: ORJSONResponse | None
    @return:
    """
    try:
        JaegerWorker.set_span_attribute(key="http.request_id", value=request.headers["X-Request-Id"])

    except KeyError:
        if settings.is_prod_env:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Request-Id is required")
