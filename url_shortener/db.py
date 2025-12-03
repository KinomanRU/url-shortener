import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import config
from models import Base

engine = create_async_engine(config.get("DB", "URL"))

new_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def drop_all():
    if input("Are you sure you want to drop all tables? [y/N]: \n").lower() == "y":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("All tables dropped")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(drop_all())
