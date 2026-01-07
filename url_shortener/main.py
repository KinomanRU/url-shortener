import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import log_utils
from config import BASE_DIR
from db import engine
from limiter import get_redis, RateLimiter, get_rate_limiter
from models import Base
from schemas import LinkSchema
from service import get_slug_by_url, add_url_to_db, get_url_by_slug

log = logging.getLogger(name=__name__)
log_utils.init_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis = get_redis()
    yield
    await redis.aclose()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def rate_limiter_factory(
    endpoint: str,
    max_requests: int,
    window_seconds: int,
):
    async def dependency(
        request: Request,
        rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
    ):
        ip_address = request.client.host
        limited = await rate_limiter.is_limited(
            ip_address,
            endpoint,
            max_requests,
            window_seconds,
        )
        if limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
            )

    return dependency


rate_limit_sql = rate_limiter_factory("sql", 3, 5)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post(
    "/",
    response_model=LinkSchema,
    dependencies=[Depends(rate_limit_sql)],
)
async def shorten_url(request: Request):
    data: dict = await request.json()
    if "url" not in data.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing URL",
        )
    url = data["url"]
    slug: str = await get_slug_by_url(url)
    if not slug:
        try:
            slug = await add_url_to_db(url)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
    return JSONResponse(
        {
            "slug": slug,
            "url": url,
        }
    )


@app.get("/{slug}")
async def redirect_by_slug(slug: str):
    try:
        url = await get_url_by_slug(slug)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return RedirectResponse(url)


if __name__ == "__main__":
    print(asyncio.run(get_slug_by_url("https://www.google.com/")))
