from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt, JWTError

from src.db.postgres import get_session as get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserInDB, Token, LoginHistory
from src.utils.auth_service import AuthService
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
)
from src.db.redis_client import get_redis_auth
from src.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_auth_service() -> AuthService:
    redis_auth = await get_redis_auth()
    return AuthService(redis_auth)


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, db: AsyncSession = Depends(get_db)) -> UserInDB:
    existing_user = await User.get_user_by_login(db, user_create.login)
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered")

    user_create.password = get_password_hash(user_create.password)
    new_user = await User.create(db, user_create)
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    user = await User.get_user_by_login(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect login or password")

    role = user.role.value
    subscriptions = [s.name for s in user.subscriptions]

    access_token = create_access_token(user.id, role, subscriptions, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user.id, role, subscriptions, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    await auth_service.set(refresh_token, b"active", expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    await user.add_login_history(db)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    if await auth_service.is_revoke(refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or revoked")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        subscriptions: list[str] = payload.get("subscriptions", [])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    access_token = create_access_token(user_id, role, subscriptions, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh_token = create_refresh_token(user_id, role, subscriptions, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    await auth_service.set(new_refresh_token, b"active", expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    refresh_token: str,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.delete(refresh_token)
    await auth_service.set(token, settings.TOKEN_REVOKE, expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"message": "Successfully logged out"}


@router.get("/history", response_model=list[LoginHistory])
async def login_history(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> list[LoginHistory]:
    user = await User.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return await user.get_login_history()
