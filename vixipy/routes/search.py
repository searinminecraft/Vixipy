from __future__ import annotations

from quart import (
    Blueprint,
    abort,
    redirect,
    request,
    render_template,
    url_for
)

from asyncio import gather
import logging
from typing import TYPE_CHECKING
from ..api import search, get_tag_info

if TYPE_CHECKING:
    from werkzeug.datastructures import ImmutableMultiDict
    from ..types import TagInfo, SearchResultsTop, SearchResultsIllustManga, SearchResultsManga
bp = Blueprint("search", __name__)
log = logging.getLogger("vixipy.routes.search")

@bp.route("/tags/<path:query>")
async def search_main(query: str):
    args: ImmutableMultiDict = request.args
    data, tag_info = await gather(
        search("top", query, **args),
        get_tag_info(query),
    )

    data: SearchResultsTop
    tag_info: TagInfo

    log.info(data.results)
    
    return await render_template("search/main.html", data=data, tag_info=tag_info)

@bp.route("/tags/<path:query>/artworks")
async def search_artworks(query: str):
    args: ImmutableMultiDict = request.args.copy()

    page = int(args.pop("p", 1))

    data, tag_info = await gather(
        search("artworks", query, **args, p=page),
        get_tag_info(query)
    )

    return await render_template(
        "search/illust.html",
        data=data,
        tag_info=tag_info,
        page=page,
        prev=url_for("search.search_artworks", query=query, **args, p=page-1),
        next=url_for("search.search_artworks", query=query, **args, p=page+1)
    )

@bp.route("/tags/<path:query>/illustrations")
async def search_illustrations_redirect(query: str):
    return redirect(url_for("search.search_artworks", query=query, **request.args))

@bp.route("/tags/<path:query>/manga")
async def search_manga(query: str):
    args: ImmutableMultiDict = request.args.copy()

    page = int(args.pop("p", 1))

    data, tag_info = await gather(
        search("manga", query, **args, p=page),
        get_tag_info(query)
    )

    return await render_template(
        "search/manga.html",
        data=data,
        tag_info=tag_info,
        page=page,
        prev=url_for("search.search_manga", query=query, **args, p=page-1),
        next=url_for("search.search_manga", query=query, **args, p=page+1)
    )

@bp.route("/tags/<path:query>/novels")
async def search_novel(query: str):
    abort(501)