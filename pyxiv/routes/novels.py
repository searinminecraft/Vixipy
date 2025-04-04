from __future__ import annotations

from quart import (
    Blueprint,
    abort,
    g,
    render_template,
    request,
)
from ..core.novels import (
    getNovel,
    getRecommendedNovels,
    getLanding,
    getLatestNovelsFromFollowing,
    getNovelSeries,
    getNovelSeriesContents,
)
from ..core.user import getUser
from ..classes import NovelEntry, NovelSeriesEntry, NovelSeries
from asyncio import gather
from typing import TYPE_CHECKING, Dict
import logging

if TYPE_CHECKING:
    from werkzeug.datastructures import ImmutableDict
    from ..classes import Novel, User


bp = Blueprint("novels", __name__)
log = logging.getLogger("vixipy.routes.novels")


@bp.route("/novels")
async def novels_root():
    args: ImmutableDict = request.args
    mode: str = args.get("mode", "all")
    landing = await getLanding(mode, "novel")

    landing: dict

    novels: Dict[int, NovelEntry] = {}
    novel_series: Dict[int, NovelSeriesEntry] = {}
    following: list[NovelEntry] = []
    popular_novel_series: list[NovelSeriesEntry] = []
    recommmended: list[NovelEntry] = []

    for n in landing["body"]["thumbnails"]["novel"]:
        novels[int(n["id"])] = NovelEntry(n)

    for ns in landing["body"]["thumbnails"]["novelSeries"]:
        novel_series[int(ns["id"])] = NovelSeriesEntry(ns)

    for rec_id in landing["body"]["page"]["recommend"]["ids"]:
        recommmended.append(novels[int(rec_id)])

    for pop_ns_id in landing["body"]["page"]["popularSeriesIds"]:
        try:
            popular_novel_series.append(novel_series[int(pop_ns_id)])
        except Exception:
            log.warn(
                "%d in popularSeriesIds, but not in our novel_series", int(pop_ns_id)
            )

    for follow_n_id in landing["body"]["page"]["follow"]:
        try:
            following.append(novels[int(follow_n_id)])
        except Exception:
            log.debug(novels)
            log.warn(
                "%d in follow, but not in our novels", int(follow_n_id)
            )

    log.debug((
        "Status: Novels: %d, "
        "Novel Series: %d, "
        "Popular Series: %d, "
        "Recommended: %d, "
        "Following: %d"
        ),
        len(novels),
        len(novel_series),
        len(popular_novel_series),
        len(recommmended),
        len(following)
    )

    return await render_template("novels/index.html", recommended=recommmended, popular_novel_series=popular_novel_series, following=following)


@bp.route("/novels/<int:id>")
async def novel_main(id: int):
    data = await getNovel(id)
    user, recommended = await gather(
        getUser(data.userId, False),
        getRecommendedNovels(id),
    )

    data: Novel
    user: User
    recommended: list[NovelEntry]

    return await render_template("novels/novel.html", data=data, user=user, recommended=recommended)

@bp.route("/novels/series/<int:id>")
async def novel_series(id: int):
    p = int(request.args.get("p", 1))
    series, content = await gather(
        getNovelSeries(id),
        getNovelSeriesContents(id, p)
    )
    series: NovelSeries
    content: list[NovelEntry]

    x, y = divmod(series.total, 30)
    total = x
    if y >= 1:
        total += 1

    return await render_template("novels/series.html", data=series, content=content, total=total)