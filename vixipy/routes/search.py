from __future__ import annotations

from quart import Blueprint, abort, redirect, request, render_template, url_for
from quart_rate_limiter import limit_blueprint, timedelta, RateLimit, rate_limit

from asyncio import gather
import logging
import random
from typing import TYPE_CHECKING
from urllib.parse import quote
from ..api import pixiv_request, search, get_tag_info
from ..filters import filter_from_prefs as ff
from ..filters import check_blacklisted_tag
from ..lib.scrapes import get_popular_tags
from ..types import ArtworkEntry, RecommendByTag, TagTranslation

if TYPE_CHECKING:
    from werkzeug.datastructures import ImmutableMultiDict
    from ..types import (
        TagInfo,
        SearchResultsTop,
        SearchResultsIllustManga,
        SearchResultsManga,
        SearchResultsNovel,
    )
    from typing import Dict, List

bp = Blueprint("search", __name__)
log = logging.getLogger("vixipy.routes.search")
limit_blueprint(
    bp,
    limits=[
        RateLimit(1, timedelta(seconds=1)),
        RateLimit(10, timedelta(seconds=30))
    ]
)


@bp.route("/tags")
@rate_limit(
    limits=[
        RateLimit(1, timedelta(seconds=5)),
        RateLimit(5, timedelta(seconds=30)),
    ]
)
async def popular_tags():
    args: ImmutableMultiDict = request.args
    novel = True if args.get("type") == "novel" else False
    data = await get_popular_tags(novel)
    return await render_template("search/popular_tags.html", data=data)


@bp.route("/tags/<path:query>")
async def search_main(query: str):
    args: ImmutableMultiDict = request.args
    if check_blacklisted_tag(query):
        abort(403)

    data, tag_info = await gather(
        search("top", query, **args),
        get_tag_info(query),
    )

    data: SearchResultsTop
    tag_info: TagInfo

    data.results = ff(data.results)
    data.novels = ff(data.novels)
    data.popular_recent = ff(data.popular_recent)
    data.popular_permanent = ff(data.popular_permanent)

    return await render_template("search/main.html", data=data, tag_info=tag_info)


@bp.route("/tags/<path:query>/artworks")
async def search_artworks(query: str):
    args: ImmutableMultiDict = request.args.copy()

    page = int(args.pop("p", 1))
    args = {
        "word": query,
        "order": "date_d",
        "mode": "safe",
        "csw": 0,
        "s_mode": "s_tag_full",
        "type": "illust_and_ugoira",
        **args,
    }

    data, tag_info = await gather(
        search("illustrations", query, **args, p=page), get_tag_info(query)
    )

    data.results = ff(data.results)

    return await render_template(
        "search/illust.html",
        data=data,
        tag_info=tag_info,
        page=page,
        prev=url_for("search.search_artworks", query=query, **args, p=page - 1),
        next=url_for("search.search_artworks", query=query, **args, p=page + 1),
    )


@bp.route("/tags/<path:query>/illustrations")
async def search_illustrations_redirect(query: str):
    return redirect(url_for("search.search_artworks", query=query, **request.args))


@bp.route("/tags/<path:query>/manga")
async def search_manga(query: str):
    args: ImmutableMultiDict = request.args.copy()

    page = int(args.pop("p", 1))

    data, tag_info = await gather(
        search("manga", query, **args, p=page), get_tag_info(query)
    )

    data.results = ff(data.results)

    return await render_template(
        "search/manga.html",
        data=data,
        tag_info=tag_info,
        page=page,
        prev=url_for("search.search_manga", query=query, **args, p=page - 1),
        next=url_for("search.search_manga", query=query, **args, p=page + 1),
    )


@bp.route("/tags/<path:query>/novels")
async def search_novel(query: str):
    args: ImmutableMultiDict = request.args.copy()

    page = int(args.pop("p", 1))

    data, tag_info = await gather(
        search("novels", query, **args, p=page), get_tag_info(query)
    )

    data.results = ff(data.results)

    return await render_template(
        "search/novel.html",
        data=data,
        tag_info=tag_info,
        page=page,
        prev=url_for("search.search_novel", query=query, **args, p=page - 1),
        next=url_for("search.search_novel", query=query, **args, p=page + 1),
    )


class RecommendTag:
    def __init__(self, d, illust, tt=None):
        self.tag: str = d["tag"]
        self.translation: TagTranslation = tt
        self.illust: ArtworkEntry = illust


@bp.route("/search", methods=["GET", "POST"])
async def search_dashboard():
    if request.method == "POST":
        form = await request.form
        return redirect(url_for("search.search_main", query=form["query"]))

    data = await pixiv_request("/ajax/search/suggestion", ignore_cache=True)

    _translations: Dict[str, TagTranslation] = {
        x: TagTranslation(x, data["tagTranslation"][x]) for x in data["tagTranslation"]
    }
    _illusts: Dict[int, ArtworkEntry] = {
        int(x["id"]): ArtworkEntry(x) for x in data["thumbnails"]
    }

    recommend_tags: list[RecommendTag] = []
    recommend_by_tag: list[RecommendByTag] = []

    for _pit in data["recommendTags"]["illust"]:
        recommend_tags.append(
            RecommendTag(
                _pit, _illusts[int(random.choice(_pit["ids"]))], _translations.get(_pit["tag"])
            )
        )

    for rec in data["recommendByTags"]["illust"]:
        __ids = [int(x) for x in rec["ids"]]
        __tag = rec["tag"]
        __illusts = []
        __translation = _translations.get(__tag)
        for __id in __ids:
            if il := _illusts.get(__id):
                __illusts.append(il)
        recommend_by_tag.append(RecommendByTag(ff(__illusts), __tag, __translation))

    log.debug("Recommended Tags: %s", recommend_tags)
    log.debug("Recommend By tag: %s", recommend_by_tag)

    return await render_template(
        "search/dashboard.html",
        recommend_tags=recommend_tags,
        recommend=recommend_by_tag,
    )
