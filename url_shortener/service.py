import random
import string

from config import config
from models import Link
import db_api


def generate_slug() -> str:
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=config.getint("Main", "Symbols_Num"),
        )
    )


async def get_slug_by_url(url: str) -> str:
    result = await db_api.select_row(Link, url=url)
    if result:
        return result.slug
    return ""


async def get_url_by_slug(slug: str) -> str:
    result = await db_api.select_row_by_pk(Link, slug)
    return result.url


async def add_url_to_db(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        raise ValueError('URL have to start with "http://" or "https://"')
    slug = generate_slug()
    link = Link(slug=slug, url=url)
    await db_api.insert_row(link)
    return link.slug
