from quart import Blueprint, abort, current_app, g, request, render_template

from ..api.handler import pixiv_request
from ..api.ranking import get_ranking
from ..converters import proxy
from ..filters import filter_from_prefs as ff
from ..abc.common import Tag, TagTranslation
from ..abc.artworks import RecommendByTag, ArtworkEntry

import random
import logging
from typing import Dict

bp = Blueprint("index", __name__)
log = logging.getLogger("vixipy.routes.index")


class TrendingTag:
    def __init__(self, tag: TagTranslation, rate: int, work: ArtworkEntry):
        self.tag = tag
        self.rate = rate
        self.work = work

    def __repr__(self):
        return ("<TrendingTag tag=%s" " rate=%d" " work=%s>") % (
            self.tag,
            self.rate,
            self.work,
        )


class _Pixivision:
    def __init__(self, id: int, title: str, thumb: str):
        self.id: int = int(id)
        self.title: str = title
        self.thumb = proxy(thumb)


@bp.get("/")
async def index():
    if g.authorized:
        mode = request.args.get("mode", "all")
        if mode not in ("all", "r18"):
            abort(400)

        if mode == "r18" and (
            current_app.config["NO_R18"] or current_app.config["NO_SENSITIVE"]
        ):
            abort(403)

        tag_translations: Dict[str, TagTranslation] = {}
        illusts: Dict[int, ArtworkEntry] = {}
        following: list[ArtworkEntry] = []
        recommend: list[ArtworkEntry] = []
        recommend_by_tag: list[RecommendBytag] = []
        new: list[ArtworkEntry] = []
        tags: list[TagTranslation] = []
        trending_tags: list[TrendingTag] = []
        pixivision: list[_Pixivision] = []

        data = await pixiv_request(
            "/ajax/top/illust", params=[("mode", mode)], ignore_cache=True
        )

        _page = data["page"]
        _tag_translations = data["tagTranslation"]
        _tags = _page["myFavoriteTags"] + [x["tag"] for x in _page["tags"]]
        _trending_tags = _page["trendingTags"]
        _recommend = [int(x) for x in _page["recommend"]["ids"]]
        _illusts = data["thumbnails"]["illust"]
        _following = _page["follow"]
        _recommend_by_tag = _page["recommendByTag"]
        _new_post = [int(x) for x in _page["newPost"]]
        _pixivision = _page["pixivision"]

        for tag in _tag_translations:
            tag_translations[tag] = TagTranslation(tag, _tag_translations[tag])

        for illust in _illusts:
            illusts[int(illust["id"])] = ArtworkEntry(illust)

        for f in _following:
            if il := illusts.get(f):
                following.append(il)

        for r in _recommend:
            if il := illusts.get(r):
                recommend.append(il)

        for n in _new_post:
            if il := illusts.get(n):
                new.append(il)

        for tr in _trending_tags:
            il = illusts.get(random.choice(tr["ids"]))
            rate = tr["trendingRate"]
            tag = tag_translations.get(
                tr["tag"],
                TagTranslation(
                    tr["tag"],
                    {x: None for x in ("en", "ko", "zh", "zh_tw", "romaji")},
                ),
            )
            res = TrendingTag(tag, rate, il)
            trending_tags.append(res)
            log.debug(res)

        for rec in _recommend_by_tag:
            __ids = [int(x) for x in rec["ids"]]
            __tag = rec["tag"]
            __illusts = []
            __translation = tag_translations.get(__tag)

            for __id in __ids:
                if il := illusts.get(__id):
                    __illusts.append(il)

            recommend_by_tag.append(RecommendByTag(ff(__illusts), __tag, __translation))

        for t in _tags:
            tags.append(
                tag_translations.get(
                    t,
                    TagTranslation(
                        t,
                        {x: None for x in ("en", "ko", "zh", "zh_tw", "romaji")},
                    ),
                )
            )

        for px in _pixivision:
            pixivision.append(_Pixivision(px["id"], px["title"], px["thumbnailUrl"]))

        return await render_template(
            "index.html.j2",
            following=ff(following),
            recommend=ff(recommend),
            rec_tag=recommend_by_tag,
            new=ff(new),
            tags=tags,
            trending_tags=trending_tags,
            pixivision=pixivision,
        )

    else:
        data = await get_ranking()
        return await render_template("index_logged_out.html.j2", data=data)
