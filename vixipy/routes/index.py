from quart import Blueprint, abort, g, request, render_template

from ..api import pixiv_request, get_ranking
from ..filters import filter_from_prefs as ff
from ..types import Tag, ArtworkEntry, TagTranslation, RecommendByTag

from typing import Dict

bp = Blueprint("index", __name__)


@bp.get("/")
async def index():
    if g.authorized:
        mode = request.args.get("mode", "all")
        if mode not in ("all", "r18"):
            abort(400)

        tag_translations: Dict[str, TagTranslation] = {}
        illusts: Dict[int, ArtworkEntry] = {}
        following: list[ArtworkEntry] = []
        recommend: list[ArtworkEntry] = []
        recommend_by_tag: list[RecommendBytag] = []
        new: list[ArtworkEntry] = []

        data = await pixiv_request("/ajax/top/illust", params=[("mode", mode)], ignore_cache=True)

        _page = data["page"]
        _tag_translations = data["tagTranslation"]
        _recommend = [int(x) for x in _page["recommend"]["ids"]]
        _illusts = data["thumbnails"]["illust"]
        _following = _page["follow"]
        _recommend_by_tag = _page["recommendByTag"]
        _new_post = [int(x) for x in _page["newPost"]]

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

        for rec in _recommend_by_tag:
            __ids = [int(x) for x in rec["ids"]]
            __tag = rec["tag"]
            __illusts = []
            __translation = tag_translations.get(__tag)

            for __id in __ids:
                if il := illusts.get(__id):
                    __illusts.append(il)

            recommend_by_tag.append(RecommendByTag(__illusts, __tag, __translation))

        return await render_template(
            "index.html",
            following=ff(following),
            recommend=ff(recommend),
            rec_tag=recommend_by_tag,
            new=ff(new),
        )
    else:
        data = await get_ranking()
        return await render_template("index_logged_out.html", data=data)
