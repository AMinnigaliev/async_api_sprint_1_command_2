# src/services/oauth_service.py

import httpx
from typing import Literal
from src.core.config import settings

OAUTH_PROVIDERS = Literal["google", "yandex", "vk"]


class OAuthService:
    def __init__(self, provider: OAUTH_PROVIDERS):
        self.provider = provider
        self.client_id = settings.oauth[provider]["client_id"]
        self.client_secret = settings.oauth[provider]["client_secret"]
        self.redirect_uri = settings.oauth[provider]["redirect_uri"]
        self.token_url = settings.oauth[provider]["token_url"]
        self.user_info_url = settings.oauth[provider]["user_info_url"]

    async def get_access_token(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            if self.provider == "vk":
                response = await client.get(self.token_url, params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": code
                })
            else:
                response = await client.post(self.token_url, data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                })
            response.raise_for_status()
            data = response.json()
            if self.provider == "vk":
                self._vk_email = data.get("email")
            return data["access_token"]

    async def get_user_info(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"} if self.provider != "vk" else {}
            if self.provider == "vk":
                response = await client.get(self.user_info_url, params={"access_token": token})
                response.raise_for_status()
                data = response.json()
                user = data["response"][0]
                user["email"] = self._vk_email
                return user
            else:
                response = await client.get(self.user_info_url, headers=headers)
                response.raise_for_status()
                return response.json()


# src/api/v1/social_auth.py

from fastapi import APIRouter, Request, Depends, HTTPException
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
        f"{conf['authorize_url']}?response_type=code&client_id={conf['client_id']}"
        f"&redirect_uri={conf['redirect_uri']}&scope={conf['scope']}"
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


# src/services/user_service.py (добавить в конец)

from src.models import User


async def get_or_create_oauth_user(user_data: dict, provider: str):
    email = user_data.get("email") or f"{provider}_{user_data['id']}@oauth.local"
    user = await User.get_by_email(email)
    if not user:
        full_name = user_data.get("name") or user_data.get("first_name") or provider
        user = await User.create(email=email, name=full_name, oauth_provider=provider)
    return user


# src/core/config.py (в конец OAuth часть)

from pydantic import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    ...
    oauth: Dict[str, Dict[str, str]] = {
        "google": {
            "client_id": "your-google-client-id",
            "client_secret": "your-google-secret",
            "redirect_uri": "http://localhost:8000/auth/social/callback/google",
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo",
            "scope": "email profile"
        },
        "yandex": {
            "client_id": "your-yandex-client-id",
            "client_secret": "your-yandex-secret",
            "redirect_uri": "http://localhost:8000/auth/social/callback/yandex",
            "authorize_url": "https://oauth.yandex.ru/authorize",
            "token_url": "https://oauth.yandex.ru/token",
            "user_info_url": "https://login.yandex.ru/info",
            "scope": "login:email login:info"
        },
        "vk": {
            "client_id": "your-vk-client-id",
            "client_secret": "your-vk-secret",
            "redirect_uri": "http://localhost:8000/auth/social/callback/vk",
            "authorize_url": "https://oauth.vk.com/authorize",
            "token_url": "https://oauth.vk.com/access_token",
            "user_info_url": "https://api.vk.com/method/users.get?fields=uid,first_name,last_name,email&v=5.131",
            "scope": "email"
        },
    }


settings = Settings()

# Регистрация router
# app.include_router(social_auth.router)
