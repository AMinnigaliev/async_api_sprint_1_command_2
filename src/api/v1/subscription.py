from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.postgres import get_session
from src.models.user import Subscription, UserRoleEnum
from src.schemas.user import SubscriptionCreateUpdate, SubscriptionResponse
from src.services.auth_service import check_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/", response_model=list[SubscriptionResponse])
async def get_subscriptions(
        db: AsyncSession = Depends(get_session)
) -> tuple[Subscription]:
    """Эндпоинт для получения всех подписок."""
    result = await db.execute(select(Subscription))
    return result.scalars().all()


@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    create_data: SubscriptionCreateUpdate,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> Subscription:
    """Эндпоинт для создания новой подписки."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await check_token(token, (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN))

    subscription = Subscription(**create_data.model_dump())

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def subscription_update(
    subscription_id: UUID,
    update_data: SubscriptionCreateUpdate,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> Subscription:
    """Эндпоинт для изменения подписки."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await check_token(token, (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN))

    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(subscription, key, value)

    await db.commit()
    await db.refresh(subscription)

    return subscription


@router.delete("/{subscription_id}")
async def delete_role(
    subscription_id: UUID,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Эндпоинт для удаления подписки."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await check_token(token, (UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN))

    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    await db.delete(subscription)
    await db.commit()
    return {"message": "Subscription deleted"}
