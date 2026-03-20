import ssl as _ssl
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Fly.io internal network: use connect_args to disable SSL for asyncpg
_connect_args: dict = {}
if ".flycast" in settings.database_url or ".internal" in settings.database_url:
    _connect_args["ssl"] = False

engine = create_async_engine(settings.database_url, echo=settings.debug, connect_args=_connect_args)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
