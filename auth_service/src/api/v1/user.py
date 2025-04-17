from fastapi import APIRouter, Depends, status, Query, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from functools import lru_cache
from fastapi.responses import RedirectResponse

from src.dependencies.auth import oauth2_scheme
from src.schemas.login_history import LoginHistory
from src.schemas.token import Token
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services.user_service import UserService, get_user_service
from src.services.oauth_service import YandexOAuthService
from src.services.auth_service import AuthService
from src.core.config import settings

router = APIRouter()


@lru_cache()
def get_oauth_service() -> YandexOAuthService:
    """
    Провайдер для YandexOAuthService.
    """
    return YandexOAuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя с логином, паролем и профилем. Возвращает объект пользователя."
)
async def register_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Регистрирует нового пользователя.
    """
    return await user_service.create_user(user_create)


@router.post(
    "/login",
    response_model=Token,
    summary="Аутентификация пользователя",
    description="Проверяет логин и пароль. Возвращает access и refresh токены."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> Token:
    """
    Аутентифицирует пользователя и возвращает JWT токены.
    """
    return await user_service.login_user(
        form_data.username, form_data.password
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление access-токена",
    description="Обновляет access-токен при валидном refresh-токене. Возвращает новые токены."
)
async def refresh_token(
    refresh_token: str,
    user_service: UserService = Depends(get_user_service),
) -> Token:
    """
    Обновляет access и refresh токены, если refresh валиден.
    """
    return await user_service.refresh_tokens(refresh_token)


@router.patch(
    "/update",
    response_model=UserResponse,
    summary="Обновление данных пользователя",
    description="Позволяет пользователю изменить логин и/или пароль без подтверждения email."
)
async def update_user(
    user_update: UserUpdate,
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await user_service.update_user(token, user_update)


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Удаляет refresh токен и отзывает access токен."
)
async def logout(
    refresh_token: str,
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> dict[str, str]:
    """
    Удаляет refresh и отзывает access токен.
    """
    await user_service.logout_user(token, refresh_token)
    return {"message": "Successfully logged out"}


@router.get(
    "/history",
    response_model=list[LoginHistory],
    summary="История входов пользователя",
    description="Возвращает список логинов пользователя по токену."
)
async def login_history(
    token: str = Depends(oauth2_scheme),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Кол-во записей",
    ),
    page_number: int = Query(
        default=1,
        ge=1,
        description="Пагинация",
    ),
    user_service: UserService = Depends(get_user_service),
) -> list[LoginHistory]:
    """
    Возвращает историю входов пользователя.
    """
    return await user_service.get_login_history(token=token, page_size=page_size, page_number=page_number)


@router.get(
    "/social/login/yandex",
    summary="Перенаправляет на Yandex OAuth"
)
async def login_yandex():
    """
    Формирует URL авторизации Yandex и перенаправляет на него.
    """
    # Базовый URL теперь в настройках
    base_auth_url = settings.yandex_auth_url
    # Собираем query-параметры
    params = (
        f"?response_type=code"
        f"&client_id={settings.yandex_client_id}"
        f"&redirect_uri={settings.yandex_redirect_uri}"
    )
    redirect_url = base_auth_url + params
    return RedirectResponse(redirect_url)


@router.get(
    "/social/callback/yandex",
    response_model=Token,
    summary="Колбэк от Yandex OAuth"
)
async def callback_yandex(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    oauth_service: YandexOAuthService = Depends(get_oauth_service),
) -> Token:
    """
    Обработка колбэка от Yandex: получение токена, инфо о пользователе и выдача JWT.
    """
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    token = await oauth_service.get_access_token(code)
    user_info = await oauth_service.get_user_info(token)

    email = user_info.get("default_email")
    yandex_id = user_info.get("id")
    username = user_info.get("login") or f"user_{yandex_id}"

    user = await user_service.get_or_create_oauth_user(
        email=email, oauth_id=yandex_id, username=username
    )
    return await user_service.login_user_oauth(user)
