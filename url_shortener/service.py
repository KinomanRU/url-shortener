import random
import string

from sqlalchemy import select

from config import config
from db import new_session
from models import Link


def generate_slug() -> str:
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=config.getint("Main", "Symbols_Num"),
        )
    )


async def get_slug_by_url(url: str) -> str:
    query = select(Link.slug).filter_by(url=url)
    async with new_session() as session:
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_url_by_slug(slug: str) -> str:
    async with new_session() as session:
        result = await session.get(Link, slug)
        if not result:
            raise ValueError(f"{slug!r} is not a valid slug")
        return result.url


async def add_url_to_db(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        raise ValueError('URL have to start with "http://" or "https://"')
    slug = generate_slug()
    link = Link(slug=slug, url=url)
    async with new_session() as session:
        session.add(link)
        await session.commit()
    return link.slug
