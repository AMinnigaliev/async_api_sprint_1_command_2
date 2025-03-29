from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.db.postgres import get_session as get_db
from src.schemas.user import UserCreate, UserInDB, Token, LoginHistory, UserUpdate
from src.services.auth_service import AuthService
from src.db.redis_client import get_redis_auth
from src.services.user_service import UserService
from src.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_auth_service() -> AuthService:
    return await get_redis_auth()


@router.post(
    "/register",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя с логином, паролем и профилем. Возвращает объект пользователя."
)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserInDB:
    user = await UserService.create_user(user_create, db)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Аутентификация пользователя",
    description="Проверяет логин и пароль. Возвращает access и refresh токены."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await UserService.login_user(form_data.username, form_data.password, db, auth_service)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление access-токена",
    description="Обновляет access-токен при валидном refresh-токене. Возвращает новые токены."
)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await UserService.refresh_tokens(refresh_token, auth_service)


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Удаляет refresh токен и отзывает access токен."
)
async def logout(
    refresh_token: str,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await UserService.logout_user(access_token=token, refresh_token=refresh_token, auth_service=auth_service)
    return {"message": "Successfully logged out"}


@router.patch(
    "/update",
    response_model=UserInDB,
    summary="Обновление данных пользователя",
    description="Позволяет пользователю изменить логин и/или пароль без подтверждения email."
)
async def update_user(
    user_update: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserInDB:
    user = await User.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await UserService.update_user(user, user_update, db)


@router.get(
    "/history",
    response_model=list[LoginHistory],
    summary="История входов пользователя",
    description="Возвращает список логинов пользователя по токену."
)
async def login_history(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> list[LoginHistory]:
    user = await User.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await UserService.get_login_history(user)
