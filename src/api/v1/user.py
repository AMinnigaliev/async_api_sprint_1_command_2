from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
)
from src.db.postgres import get_session as get_db
from src.db.redis_client import get_redis_auth
from src.models.user import User
from src.schemas.user import LoginHistory, Token, UserCreate, UserInDB
from src.utils.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


async def get_auth_service() -> AuthService:
    """Получение экземпляра AuthService с подключением к Redis."""
    redis_auth = await get_redis_auth()
    return AuthService(redis_auth)


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate, db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя."""
    existing_user = await User.get_user_by_login(db, user_create.login)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered",
        )

    user_create.password = get_password_hash(user_create.password)
    new_user = await User.create(db, user_create)
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Аутентификация пользователя и выдача токенов."""
    user = await User.get_user_by_login(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )

    access_token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    await auth_service.set(
        refresh_token, b"active", expire=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    await user.add_login_history(db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str, auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление access-токена по refresh-токену."""
    revoked = await auth_service.is_revoke(refresh_token)
    if revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or revoked",
        )

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["sub"]
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    access_token = create_access_token(
        {"sub": str(user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    refresh_token: str, auth_service: AuthService = Depends(get_auth_service)
):
    """Выход из системы, пометка refresh-токена как отозванного."""
    await auth_service.set(
        refresh_token, b"revoked", expire=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {"message": "Successfully logged out"}


@router.get("/history", response_model=list[LoginHistory])
async def login_history(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """Получение истории входов пользователя."""
    user = await User.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await user.get_login_history()
