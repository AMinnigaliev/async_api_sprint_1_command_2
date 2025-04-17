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
            # пытаемся вытащить собственное описание ошибки от Яндекса
            try:
                err = response.json()
                error_detail = (
                    err.get("error_description")
                    or err.get("error")
                    or response.text
                )
            except ValueError:
                error_detail = response.text

            raise HTTPException(
                status_code=400,
                detail=f"Не удалось получить токен Яндекса: {error_detail}"
            )

        return response.json().get("access_token")

    async def get_user_info(self, token: str) -> dict:
        headers = {"Authorization": f"OAuth {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.USER_INFO_URL, headers=headers)

        if response.status_code != 200:
            # извлекаем сообщение об ошибке от Яндекса или возвращаем сырой текст
            try:
                err = response.json()
                error_detail = (
                    err.get("error_description")
                    or err.get("error")
                    or err.get("message")
                    or response.text
                )
            except ValueError:
                error_detail = response.text

            raise HTTPException(
                status_code=400,
                detail=f"Не удалось получить информацию о пользователе Яндекса: {error_detail}"
            )

        return response.json()
