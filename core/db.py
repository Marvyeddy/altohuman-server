from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from .config import Config as cfg
from sqlmodel.ext.asyncio import AsyncSession

async_engine = AsyncEngine(create_engine(url=cfg.DATABASE_URL, echo=False, future=True))


async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session
