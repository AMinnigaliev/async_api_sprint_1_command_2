from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.core.config import settings

Base = declarative_base()

dsn = (
    f"postgresql+asyncpg://{settings.PG_USER}:{settings.PG_PASSWORD}@"
    f"{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_NAME}"
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
