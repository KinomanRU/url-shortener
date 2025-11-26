import sys
import asyncio
import logging

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import log_utils
from config import BASE_DIR
from service import get_slug_by_url, add_url_to_db, get_url_by_slug

log = logging.getLogger(name=__name__)
log_utils.init_logging()

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/")
async def add_url(request: Request):
    data: dict = await request.json()
    if "url" not in data.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing URL"
        )
    url = data["url"]
    slug: str = await get_slug_by_url(url)
    if not slug:
        await add_url_to_db(url)
    slug = await get_slug_by_url(url)


@app.get("/{slug}")
async def index(request: Request, slug: str):
    url = await get_url_by_slug(slug)
    if not url.startswith("http"):
        url = "https://" + url
    return RedirectResponse(url=url)


if __name__ == "__main__":
    # uvicorn.run("main:app", reload=True)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(asyncio.run(get_url_by_slug("")))
