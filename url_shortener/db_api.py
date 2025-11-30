from typing import Any, Type

from sqlalchemy import select

from models import Base
from db import new_session


async def insert_row(item: Base) -> None:
    async with new_session() as session:
        session.add(item)
        await session.commit()


async def select_row_by_pk(entity: Type[Base], pk: Any) -> Base:
    async with new_session() as session:
        result = await session.get(entity, pk)
        if not result:
            raise ValueError(f"Row with primary key {pk!r} not found")
        return result


async def select_row(entity: Type[Base], *args, **kwargs) -> Base:
    query = select(entity).filter_by(**kwargs)
    async with new_session() as session:
        result = await session.execute(query)
    return result.scalar_one_or_none()
