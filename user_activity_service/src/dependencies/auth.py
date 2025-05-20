from fastapi import Depends, HTTPException, Request, status

from src.dependencies.request import get_request_id
from src.dependencies.token import get_token
from src.services.auth_service import AuthService, get_auth_service


def role_dependency(required_roles: tuple[str]):
    """
    Создаёт зависимость для проверки роли пользователя.

    Эта зависимость выполняет следующие проверки:
    1. Получает payload токена через AuthService.
    2. Сравнивает роль пользователя с переданными допустимыми ролями.
    """
    async def _check_role(
        request_id: Request = Depends(get_request_id),
        token: str = Depends(get_token),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> dict:
        payload = await auth_service.varify_token_with_cache(
            token, request_id, False)

        if payload.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

        return payload

    return _check_role


def role_dependency_exp_important(required_roles: tuple[str]):
    """
    Создаёт зависимость для проверки роли пользователя строго с учётом времени
    жизни токена.

    Эта зависимость выполняет следующие проверки:
    1. Получает payload токена через AuthService.
    2. Сравнивает роль пользователя с переданными допустимыми ролями.
    """
    async def _check_role(
        request_id: Request = Depends(get_request_id),
        token: str = Depends(get_token),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> dict:
        payload = await auth_service.varify_token_with_cache(
            token, request_id, True
        )

        if payload.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

        return payload

    return _check_role
