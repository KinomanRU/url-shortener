import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import config
from models import Base

show_sql: bool = config.getboolean("Debug", "Show_SQL")

engine = create_async_engine(
    config.get("DB", "URL"),
    echo=show_sql,
)

new_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)

if show_sql:
    logging.getLogger("sqlalchemy.engine.Engine").handlers = [logging.NullHandler()]


async def drop_all():
    if input("Are you sure you want to drop all tables? [y/N]: \n").lower() == "y":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("All tables dropped")


if __name__ == "__main__":
    asyncio.run(drop_all())
