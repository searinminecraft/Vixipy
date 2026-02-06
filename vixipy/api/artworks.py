from __future__ import annotations

import logging

from ..converters import proxy
from .handler import pixiv_request
from ..abc.artworks import (
    Artwork,
    ArtworkPage,
    ArtworkEntry,
    NewIllustResponse,
    IllustSeries,
)
from ..abc.users import PartialUser
from ..abc.comment import (
    CommentBase,
    Comment,
    CommentBaseResponse,
)

log = logging.getLogger(__name__)


class IllustSeriesData:
    def __init__(self, d: dict):

        _p = d["page"]
        _series: dict[int, IllustSeries] = {
            int(x["id"]): IllustSeries(x) for x in d["illustSeries"]
        }
        _illusts: dict[int, ArtworkEntry] = {
            int(x["id"]): ArtworkEntry(x) for x in d["thumbnails"]["illust"]
        }

        self.id: int = _p["seriesId"]
        self.main: IllustSeries = _series[self.id]
        self.is_set_cover: bool = _p["isSetCover"]
        self.other_series: IllustSeries = _series[int(_p["otherSeriesId"])]
        self.recent_updated_works: list[ArtworkEntry] = [
            _illusts[x] for x in _p["recentUpdatedWorkIds"]
        ]
        self.total: int = _p["total"]
        self.watched: bool = _p["isWatched"]
        self.notifying: bool = _p["isNotifying"]
        self.author: PartialUser = PartialUser(d["users"][0])


async def get_artwork(id: int) -> Artwork:
    data = await pixiv_request(f"/ajax/illust/{id}")
    return Artwork(data)


async def get_artwork_pages(id: int) -> list[ArtworkPage]:
    data = await pixiv_request(f"/ajax/illust/{id}/pages")
    _pages = []
    for k, page in enumerate(data):
        _pages.append(ArtworkPage(page, k + 1))
    return _pages


async def get_recommended_works(id: int) -> list[ArtworkEntry]:
    data = await pixiv_request(
        f"/ajax/illust/{id}/recommend/init", params=[("limit", "180")]
    )
    return [ArtworkEntry(x) for x in data["illusts"]]


async def get_artwork_comments(id: int, page: int = 1):
    data = await pixiv_request(
        "/ajax/illusts/comments/roots",
        params=[("illust_id", id), ("offset", (10 * page) - 10), ("limit", 10)],
        ignore_cache=True,
    )

    return CommentBaseResponse([Comment(x) for x in data["comments"]], data["hasNext"])


async def get_artwork_replies(id: int, page: int = 1):
    data = await pixiv_request(
        "/ajax/illusts/comments/replies",
        params=[("comment_id", id), ("page", page)],
        ignore_cache=True,
    )

    return CommentBaseResponse(
        [CommentBase(x) for x in data["comments"]], data["hasNext"]
    )


async def get_newest_works(
    type_: Union["illust", "manga"] = "illust",
    r18: bool = False,
    last_id: int = 0,
    limit: int = 20,
):
    data = await pixiv_request(
        "/ajax/illust/new",
        params=[
            ("last_id", last_id),
            ("limit", limit),
            ("type", type_),
            ("r18", str(r18).lower()),
        ],
        ignore_cache=True,
    )
    log.debug(data["lastId"])

    return NewIllustResponse(data)


async def get_illust_series(id: int, page: int = 1):
    data = await pixiv_request(f"/ajax/series/{id}", params=[("p", page)])
    return IllustSeriesData(data)
