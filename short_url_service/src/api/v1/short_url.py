from fastapi import APIRouter, Depends

from src.dependencies.request import get_request_id
from src.schemas.url import FullUrl, ShortUrl
from src.services.short_url_service import (ShortUrlService,
                                            get_short_url_service)

router = APIRouter()


@router.post("", dependencies=Depends(get_request_id), response_model=ShortUrl)
async def create(
    payload: FullUrl,
    short_url_service: ShortUrlService = Depends(get_short_url_service),

):
    url = str(payload.url)
    return await short_url_service.create(url)
