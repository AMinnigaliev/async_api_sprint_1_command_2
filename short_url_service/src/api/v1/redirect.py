from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from src.dependencies.request import get_request_id
from src.services.short_url_service import (ShortUrlService,
                                            get_short_url_service)

router = APIRouter()


@router.get(
    "/{code}",
    response_class=RedirectResponse,
)
async def redirect(
    code: str,
    request_id: str = Depends(get_request_id),
    short_url_service: ShortUrlService = Depends(get_short_url_service),
):
    url = short_url_service.get_url(code)

    return RedirectResponse(
        url=url,
        status_code=302,
        headers={"X-Request-Id": request_id}
    )
