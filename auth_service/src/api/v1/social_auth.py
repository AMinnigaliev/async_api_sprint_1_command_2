from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from src.services.oauth_service import OAuthService
from src.services.user_service import get_or_create_oauth_user
from src.services.token_service import create_tokens
from src.core.config import settings

router = APIRouter(prefix="/auth/social", tags=["OAuth"])

@router.get("/login/{provider}")
async def login(provider: str):
    conf = settings.oauth.get(provider)
    if not conf:
        raise HTTPException(400, "Unknown provider")

    url = (
        f"{conf['authorize_url']}?response_type=code"
        f"&client_id={conf['client_id']}"
        f"&redirect_uri={conf['redirect_uri']}"
        f"&scope={conf['scope']}"
    )
    return RedirectResponse(url)

@router.get("/callback/{provider}")
async def callback(provider: str, code: str):
    oauth = OAuthService(provider)
    access_token = await oauth.get_access_token(code)
    user_data = await oauth.get_user_info(access_token)

    user = await get_or_create_oauth_user(user_data, provider)
    tokens = await create_tokens(user)
    return JSONResponse(tokens)
