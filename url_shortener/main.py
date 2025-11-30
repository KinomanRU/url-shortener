import asyncio
import logging
import sys

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import log_utils
from config import BASE_DIR
from schemas import LinkSchema
from service import get_slug_by_url, add_url_to_db, get_url_by_slug

log = logging.getLogger(name=__name__)
log_utils.init_logging()

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, slug: str = ""):
    url = ""
    if slug:
        url = await get_url_by_slug(slug)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/", response_model=LinkSchema)
async def add_url(request: Request, response_class=HTMLResponse):
    data: dict = await request.json()
    if "url" not in data.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing URL"
        )
    url = data["url"]
    slug: str = await get_slug_by_url(url)
    if not slug:
        try:
            slug = await add_url_to_db(url)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return JSONResponse(
        {
            "slug": slug,
            "url": url,
        }
    )


@app.get("/{slug}")
async def index_w_slug(request: Request, slug: str):
    try:
        url = await get_url_by_slug(slug)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    return RedirectResponse(url)


if __name__ == "__main__":
    # uvicorn.run("main:app", reload=True)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(asyncio.run(get_slug_by_url("https://www.google.com/")))
