from __future__ import annotations

from quart import (
    Blueprint,
    request,
    render_template
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

@bp.route("/tags/<query>")
async def search_main(query: str):
    args: ImmutableMultiDict = request.args
    data, tag_info = await gather(
        search("top", query, **args),
        get_tag_info(query),
    )

    data: SearchResultsTop
    tag_info: TagInfo

    log.info(data.results)
    
    return await render_template("search/index.html", data=data, tag_info=tag_info)