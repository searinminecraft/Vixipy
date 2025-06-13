from __future__ import annotations

from quart import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for
)


from ..api import (
    get_novel,
    get_user,
    get_recommended_novels,
    get_novel_series,
    get_novel_series_contents,
)
from asyncio import gather
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import NovelSeries

bp = Blueprint("novels", __name__)


@bp.route("/novel/show/<int:id>")
async def novel_main(id: int):
    data = await get_novel(id)
    user, recommend = await gather(
        get_user(data.user_id),
        get_recommended_novels(id),
    )
    return await render_template("novels/novel.html", data=data, user=user, recommend=recommend)

@bp.route("/novel/series/<int:id>")
async def novel_series_main(id: int):
    data, contents = await gather(
        get_novel_series(id),
        get_novel_series_contents(id, int(request.args.get("p", 1)))
    )
    
    data: NovelSeries

    pages, _ = divmod(data.published_content_count, 30)
    if _ > 0:
        pages += 1
    return await render_template("novels/series.html", data=data, contents=contents, pages=pages)