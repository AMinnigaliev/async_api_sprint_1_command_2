from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from src.db.postgres import get_session as get_db
from src.models.user import User
from src.schemas.login_history import LoginHistory
from src.schemas.token import Token
from src.schemas.user import UserCreate, UserResponse
from src.services.auth_service import AuthService
from src.core.security import (
    create_access_token,
    create_refresh_token,
)
from src.db.redis_client import get_redis_auth
from src.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_auth_service() -> AuthService:
    redis_auth = await get_redis_auth()
    return redis_auth


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя с логином, паролем и профилем. "
                "Возвращает объект пользователя."
)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Регистрирует нового пользователя.
    """
    existing_user = await User.get_user_by_login(db, user_create.login)
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered")

    new_user = await User.create(db, user_create)
    return new_user


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
    """
    Аутентифицирует пользователя и возвращает JWT токены.
    """
    user = await User.get_user_by_login(db, form_data.username)
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )

    role = user.role.value
    subscriptions = await db.run_sync(
        lambda sync_session: [s.name for s in user.subscriptions]
    )

    access_token = create_access_token(user.id, role, subscriptions)
    refresh_token = create_refresh_token(user.id, role, subscriptions)

    await auth_service.set(
        refresh_token,
        settings.TOKEN_ACTIVE,
        expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    await user.add_login_history(db)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление access-токена",
    description="Обновляет access-токен при валидном refresh-токене. "
                "Возвращает новые токены."
)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    Обновляет access и refresh токены, если refresh валиден.
    """
    if not await auth_service.check_value(
            refresh_token, settings.TOKEN_ACTIVE
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or revoked",
        )

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        subscriptions: list[str] = payload.get("subscriptions", [])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    access_token = create_access_token(user_id, role, subscriptions)
    new_refresh_token = create_refresh_token(user_id, role, subscriptions)

    await auth_service.set(
        new_refresh_token,
        settings.TOKEN_ACTIVE,
        expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return Token(access_token=access_token, refresh_token=new_refresh_token)


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
    """
    Удаляет refresh и отзывает access токен.
    """
    await auth_service.revoke_token(token)
    await auth_service.delete(refresh_token)
    return {"message": "Successfully logged out"}


@router.get(
    "/history",
    response_model=list[LoginHistory],
    summary="История входов пользователя",
    description="Возвращает список логинов пользователя по токену."
)
async def login_history(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> list[LoginHistory]:
    """
    Возвращает историю входов пользователя.
    """
    user = await User.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await user.get_login_history()
