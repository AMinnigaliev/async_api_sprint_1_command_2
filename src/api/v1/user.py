from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.models.user import Subscription, User, UserRoleEnum
from src.repositories.user import get_user_by_id
from src.schemas.user import SubscriptionResponse, UserResponse
from src.services.auth_service import check_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/{user_id}/assign-role/{role}", response_model=UserResponse)
async def assign_role(
    user_id: UUID,
    role: UserRoleEnum,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
) -> User:
    """Эндпоинт для назначения пользователю роли."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await check_token(token, (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN))

    user = await get_user_by_id(db, user_id)
    user.role = role
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/{user_id}/role", response_model=str)
async def get_user_role(
        user_id: UUID,
        db: AsyncSession = Depends(get_session),
) -> str:
    """Эндпоинт для получения роли пользователя."""
    user = await get_user_by_id(db, user_id)

    return str(user.role)


@router.post(
    "/{user_id}/subscribe/{subscription_id}", response_model=UserResponse
)
async def assign_subscription(
        user_id: UUID,
        subscription_id: UUID,
        token: str = Security(oauth2_scheme),
        db: AsyncSession = Depends(get_session),
) -> User:
    """Эндпоинт для назначения подписки пользователю."""
    await check_token(token, (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN))

    user = await get_user_by_id(db, user_id)

    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if subscription in user.subscriptions:
        raise HTTPException(status_code=400, detail="User already subscribed")

    user.subscriptions.append(subscription)
    await db.commit()
    await db.refresh(user)

    return user


@router.delete(
    "/{user_id}/unsubscribe/{subscription_id}", response_model=UserResponse
)
async def remove_subscription(
        user_id: UUID,
        subscription_id: UUID,
        token: str = Security(oauth2_scheme),
        db: AsyncSession = Depends(get_session),
) -> User:
    """Эндпоинт для отмены подписки у пользователя."""
    await check_token(token, (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN))

    user = await get_user_by_id(db, user_id)

    subscription = await db.get(Subscription, subscription_id)
    if not subscription or subscription not in user.subscriptions:
        raise HTTPException(
            status_code=400, detail="User is not subscribed to this"
        )

    user.subscriptions.remove(subscription)
    await db.commit()
    await db.refresh(user)

    return user


@router.get(
    "/{user_id}/subscriptions", response_model=list[SubscriptionResponse]
)
async def get_user_subscriptions(
        user_id: UUID,
        token: str = Security(oauth2_scheme),
        db: AsyncSession = Depends(get_session),
) -> list[Subscription]:
    """Эндпоинт для получения списка подписок пользователя."""
    await check_token(token, (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN))

    user = await get_user_by_id(db, user_id)

    return user.subscriptions
