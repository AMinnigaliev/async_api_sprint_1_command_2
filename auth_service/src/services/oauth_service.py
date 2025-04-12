import httpx
from fastapi import HTTPException
from src.core.config import settings


class YandexOAuthService:
    TOKEN_URL = "https://oauth.yandex.ru/token"
    USER_INFO_URL = "https://login.yandex.ru/info"

    async def get_access_token(self, code: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.yandex_client_id,
            "client_secret": settings.yandex_client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.TOKEN_URL, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Yandex token")
        return response.json().get("access_token")

    async def get_user_info(self, token: str) -> dict:
        headers = {"Authorization": f"OAuth {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Yandex user info")
        return response.json()
