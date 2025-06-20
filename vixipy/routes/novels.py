from __future__ import annotations

from quart import Blueprint, render_template, redirect, request, url_for


from ..api import (
    get_novel,
    get_user,
    get_recommended_novels,
    get_novel_series,
    get_novel_series_contents,
    pixiv_request,
)
from ..filters import filter_from_prefs as ff
from ..types import NovelEntry, NovelSeriesEntry
from asyncio import gather
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import NovelSeries

bp = Blueprint("novels", __name__)


class NovelRanking:
    def __init__(self, date: str, entries: list[NovelEntry]):
        self.date: datetime = datetime.strptime(date, "%Y-%m-%d")
        self.entries: list[NovelEntry] = entries


class EditorRecommend:
    def __init__(self, novel: NovelEntry, comment: str):
        self.novel: NovelEntry = novel
        self.comment: str = comment


@bp.route("/novel")
async def novel_root():
    mode = request.args.get("mode", "all")
    data = await pixiv_request(
        "/ajax/top/novel", params=[("mode", mode)], ignore_cache=True
    )

    __page = data["page"]

    __novel_series = {
        int(x["id"]): NovelSeriesEntry(x) for x in data["thumbnails"]["novelSeries"]
    }
    __novels = {int(x["id"]): NovelEntry(x) for x in data["thumbnails"]["novel"]}

    from_followed: list[NovelEntry] = []
    popular_orig: list[NovelSeriesEntry] = []
    recommend: list[NovelEntry] = [__novels[int(x)] for x in __page["recommend"]["ids"]]
    editor_recommend: EditorRecommend = [
        EditorRecommend(__novels[int(x["novelId"])], x["comment"])
        for x in __page["editorRecommend"]
    ]

    for x in __page["follow"]:
        if novel := __novels.get(x):
            from_followed.append(novel)

    for x in __page["popularSeriesIds"]:
        if series := __novel_series.get(int(x)):
            popular_orig.append(series)

    _ranking_data = __page["ranking"]
    _ranking_date: str = _ranking_data["date"]
    _ranking: list[NovelEntry] = []

    for x in _ranking_data["items"]:
        if novel := __novels.get(int(x["id"])):
            _ranking.append(novel)

    ranking = NovelRanking(_ranking_date, ff(_ranking))

    _gender_ranking = __page["genderRanking"]

    _ranking_m_data = _gender_ranking["male"]
    _ranking_m_date: str = _ranking_m_data["date"]
    _ranking_m: list[NovelEntry] = []

    for x in _ranking_m_data["items"]:
        if novel := __novels.get(int(x["id"])):
            _ranking_m.append(novel)

    ranking_m = NovelRanking(_ranking_m_date, ff(_ranking_m))

    _ranking_f_data = _gender_ranking["female"]
    _ranking_f_date: str = _ranking_f_data["date"]
    _ranking_f: list[NovelEntry] = []

    for x in _ranking_f_data["items"]:
        if novel := __novels.get(int(x["id"])):
            _ranking_f.append(novel)

    ranking_f = NovelRanking(_ranking_f_date, ff(_ranking_f))

    return await render_template(
        "novels/index.html",
        followed=ff(from_followed),
        popular=ff(popular_orig),
        recommend=ff(recommend),
        ranking=ranking,
        ranking_m=ranking_m,
        ranking_f=ranking_f,
        editor_recommend=editor_recommend,
    )


@bp.route("/novel/show/<int:id>")
async def novel_main(id: int):
    data = await get_novel(id)
    user, recommend = await gather(
        get_user(data.user_id),
        get_recommended_novels(id),
    )
    return await render_template(
        "novels/novel.html", data=data, user=user, recommend=ff(recommend)
    )


@bp.route("/novel/series/<int:id>")
async def novel_series_main(id: int):
    data, contents = await gather(
        get_novel_series(id),
        get_novel_series_contents(id, int(request.args.get("p", 1))),
    )

    data: NovelSeries

    pages, _ = divmod(data.published_content_count, 30)
    if _ > 0:
        pages += 1
    return await render_template(
        "novels/series.html", data=data, contents=contents, pages=pages
    )


@bp.route("/novel/show.php")
async def pixivcompat_novel():
    id_ = request.args["id"]
    return redirect(url_for("novels.novel_main", id=id_))
