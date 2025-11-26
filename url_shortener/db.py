import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi import Depends

from config import config
from models import Base

engine = create_async_engine(config.get("DB", "URL"))

new_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Depends(get_session)


async def ddl():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(ddl())
