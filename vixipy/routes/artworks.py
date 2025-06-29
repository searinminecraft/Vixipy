from __future__ import annotations

from quart import Blueprint, abort, current_app, render_template, request
from quart_rate_limiter import limit_blueprint, timedelta, RateLimit
from asyncio import gather
import datetime
import logging
import re
from typing import TYPE_CHECKING

from ..api import (
    get_artwork,
    get_artwork_pages,
    get_artwork_comments,
    get_artwork_replies,
    get_recommended_works,
    get_user,
    get_user_illusts_from_ids,
)
from ..filters import filter_from_prefs as ff
from ..filters import check_blacklisted_tag
from ..types import ArtworkPage

if TYPE_CHECKING:
    from ..types import Artwork, ArtworkEntry, PartialUser
    from aiohttp import ClientResponse

bp = Blueprint("artworks", __name__)
log = logging.getLogger("vixipy.routes.artworks")
thumb_reg = re.compile(
    r"https?:\/\/i.pximg.net\/c\/.+\/img\/(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2})\/(\d+)_p(\d+)_.+\.(jpg|png)"
)

limit_blueprint(bp, limits=[RateLimit(3, timedelta(seconds=1)), RateLimit(30, timedelta(minutes=1))])


async def __attempt_work_extraction(
    id: int, userIllusts: list[ArtworkEntry], pagesCount: int
):
    uil_to_dict: list[ArtworkEntry] = {int(i.id): i for i in userIllusts}
    result: list[ArtworkPage] = []

    def pz(n: int):
        if n >= 10:
            return n
        else:
            return "0" + str(n)

    log.debug(uil_to_dict)
    if id in uil_to_dict:
        log.debug(uil_to_dict[id].unproxied_thumb)
        extracted_thumb = thumb_reg.search(uil_to_dict[id].unproxied_thumb)
        if not extracted_thumb:
            log.debug("Failed to extract date from thumbnail. Trying create date...")
            d = datetime.datetime.fromisoformat(uil_to_dict[id].uploadDate_raw)

            _date = f"{d.year}/{pz(d.month)}/{pz(d.day)}/{pz(d.hour)}/{pz(d.minute)}/{pz(d.second)}"
        else:
            _date = extracted_thumb.group(1)

        for x in range(pagesCount):
            _master = f"/img-master/img/{_date}/{id}_p{x}_master1200.jpg"
            _orig = None
            for ext in ("jpg", "png"):
                _orig_uri = f"/img-original/img/{_date}/{id}_p{x}.{ext}"

                log.debug("Trying %s", _orig_uri)
                ori: ClientResponse = await current_app.content_proxy.head(
                    "https://i.pximg.net" + _orig_uri
                )
                if ori.status != 200:
                    log.debug("Did not work!")
                    continue
                else:
                    log.debug("%s works!", _orig_uri)
                    _orig = _orig_uri
                    break

            result.append(
                ArtworkPage(
                    {
                        "urls": {
                            "regular": "i.pximg.net" + _master,
                            "original": "i.pximg.net" + _orig,
                        },
                        "width": "(unknown)",
                        "height": "(unknown)",
                    },
                    x + 1,
                )
            )

        return result
    else:
        log.info("Work not in userIllusts, cannot continue!")
        return []


@bp.get("/artworks/<int:id>")
async def _get_artwork(id: int):
    work: Artwork = await get_artwork(id)

    if any([check_blacklisted_tag(x.name) for x in work.tags]):
        abort(403)

    if work.ai and bool(int(request.cookies.get("Vixipy-No-AI", 0))):
        abort(404)

    if (
        (
            (current_app.config["NO_R18"] or current_app.config["NO_SENSITIVE"])
            and work.xrestrict >= 1
        )
        or (bool(int(request.cookies.get("Vixipy-No-R18", 0))) and work.xrestrict >= 1)
        or (bool(int(request.cookies.get("Vixipy-No-R18G", 1))) and work.xrestrict == 2)
    ):
        abort(404)

    if work.deficient:
        log.info("Work is deficient, trying to extract pages...")
        pages, recommend, user, works = await gather(
            __attempt_work_extraction(id, work.other_works, work.pages),
            get_recommended_works(id),
            get_user(work.authorId),
            get_user_illusts_from_ids(work.authorId, work.works_missing[:50]),
        )
    else:
        pages, recommend, user, works = await gather(
            get_artwork_pages(id),
            get_recommended_works(id),
            get_user(work.authorId),
            get_user_illusts_from_ids(work.authorId, work.works_missing[:50]),
        )

    pages: list[ArtworkPage]
    recommend: list[ArtworkEntry]
    user: PartialUser
    works: list[ArtworkEntry]

    if len(pages) == 0:
        abort(404)

    return await render_template(
        "artworks.html",
        work=work,
        pages=pages,
        recommend=ff(recommend),
        user=user,
        user_works=ff(sorted(works + work.other_works, key=lambda _: int(_.id))),
    )


@bp.get("/artworks/<int:id>/comments")
async def get_comments(id: int):
    data = await get_artwork_comments(id, int(request.args.get("p", 1)))
    return await render_template("comments.html", data=data, id=id)


@bp.get("/artworks/replies/<int:id>")
async def get_replies(id: int):
    data = await get_artwork_replies(id, int(request.args.get("p", 1)))
    return await render_template("replies.html", data=data, id=id)
