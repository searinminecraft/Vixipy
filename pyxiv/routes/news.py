from quart import Blueprint, render_template, request
from ..core.news import getNewsEntry, getNews, getNewsByCategory
import logging

log = logging.getLogger("vixipy.routes.news")

bp = Blueprint("news", __name__, url_prefix="/news")


@bp.route("/<int:id>")
async def getEntry(id: int):
    data = await getNewsEntry(id)
    return await render_template("news/entry.html", data=data)


@bp.route("/")
async def root():
    if cid := request.args.get("cid"):
        data = await getNewsByCategory(int(cid))
        log.debug(data)
        return await render_template("news/category.html", data=data)
    else:
        data = await getNews()
        log.debug(data)
        return await render_template("news/index.html", data=data)
