from __future__ import annotations

from .common import Tag
from ..converters import proxy, convert_pixiv_link
from bs4 import BeautifulSoup
from datetime import datetime
import markupsafe
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .common import TagTranslation


class NewIllustResponse:
    def __init__(self, d):
        self.last_id: int = int(d["lastId"])
        self.illusts: list[ArtworkEntry] = [ArtworkEntry(x) for x in d["illusts"]]


class ArtworkPage:
    def __init__(self, d, page):
        self.reg = proxy(d["urls"]["regular"])
        self.orig = proxy(d["urls"]["original"])
        self.width = d["width"]
        self.height = d["height"]
        self.page = page


class ArtworkBase:
    def __init__(self, d):
        self.id = d["id"]
        self.title = d["title"]
        self.description = d["description"]
        self.type = d["illustType"]
        self.uploadDate_raw = d["createDate"]
        self.bookmarked = d.get("bookmarkData") is not None
        self.bookmark_id = d["bookmarkData"]["id"] if d.get("bookmarkData") else None
        self.bookmark_private = (
            d["bookmarkData"]["private"] if d.get("bookmarkData") else False
        )
        self.uploadDate = datetime.fromisoformat(self.uploadDate_raw)
        self.xrestrict = d["xRestrict"]
        self.r18 = self.xrestrict >= 1
        self.r18g = self.xrestrict == 2
        self.sl = d["sl"]
        self.sensitive = self.sl >= 4
        self.alt = d["alt"]
        self.authorId = d["userId"]
        self.authorName = d["userName"]
        self.pages = int(d["pageCount"])
        self.ai = int(d["aiType"]) == 2
        self.isUgoira: bool = self.type == 2

        self.json: dict = d

    @property
    def xrestrict_friendlyname(self):
        names = {1: "R-18", 2: "R-18G"}

        return names.get(int(self.xrestrict), "R-18")


class _ArtworkImages:
    def __init__(self, d: dict):
        self.mini: Optional[str] = proxy(d["mini"])
        self.thumb: Optional[str] = proxy(d["thumb"])
        self.small: Optional[str] = proxy(d["small"])
        self.regular: Optional[str] = proxy(d["regular"])
        self.original: Optional[str] = proxy(d["original"])


class _SeriesNav:
    def __init__(self, d: dict):
        self.id: int = int(d["id"])
        self.title: str = d["title"]
        self.order: int = d["order"]


class _SeriesNavData:
    def __init__(self, d: dict):
        self.id: int = int(d["seriesId"])
        self.title: str = d["title"]
        self.order: int = d["order"]
        self.watched: bool = d["isWatched"]
        self.notifying: bool = d["isNotifying"]
        self.prev: Optional[_SeriesNav] = _SeriesNav(d["prev"]) if d["prev"] else None
        self.next: Optional[_SeriesNav] = _SeriesNav(d["next"]) if d["next"] else None


class Artwork(ArtworkBase):
    def __init__(self, d):
        super().__init__(d)
        self.tags: list[Tag] = []
        for t in d["tags"]["tags"]:
            if _r := t.get("romaji"):
                _romaji = _r
            else:
                _romaji = None
            if _t := t.get("translation"):
                _en = _t["en"]
            else:
                _en = None

            self.tags.append(Tag(t["tag"], _en, _romaji))

        self.thumb = proxy(d["urls"]["regular"])
        self.authorHandle = d["userAccount"]
        self.width = d["width"]
        self.height = d["height"]
        self.bookmarkCount = d["bookmarkCount"]
        self.likeCount = d["likeCount"]
        self.liked = d["likeData"]
        self.commentCount = d["commentCount"]
        self.viewCount = d["viewCount"]
        self.image_urls: _ArtworkImages = _ArtworkImages(d["urls"])
        self.deficient = self.image_urls.regular is None
        self.series_data: Optional[_SeriesNavData] = (
            _SeriesNavData(d["seriesNavData"]) if d["seriesNavData"] else None
        )

        self.original = d["isOriginal"]
        self.loginonly = d["isLoginOnly"]
        self.ai = d["aiType"] == 2

        _description = d["illustComment"]
        self.description_stripped = markupsafe.Markup(_description).striptags()
        _s = BeautifulSoup(_description, "html.parser")
        for x in _s.find_all("a"):
            href = x.attrs["href"]
            x.attrs["href"] = convert_pixiv_link(href)
            if x.attrs.get("target"):
                del x.attrs["target"]

        self.description = _s

        self.other_works: list[ArtworkEntry] = []
        self.works_missing: list[int] = []

        for x in d["userIllusts"]:
            if d["userIllusts"][x] is None:
                self.works_missing.append(int(x))
            else:
                self.other_works.append(ArtworkEntry(d["userIllusts"][x]))


class ArtworkEntry(ArtworkBase):
    def __init__(self, d):
        super().__init__(d)
        self.unproxied_thumb = d["url"]
        self.thumb = proxy(self.unproxied_thumb)
        self.profileimg = proxy(d.get("profileImageUrl"))
        self.tags: list[str] = d.get("tags", [])

    def __repr__(self):
        return f"<ArtworkEntry {self.id}>"


class RecommendByTag:
    def __init__(
        self, illusts: list[ArtworkEntry], name: str, translation: TagTranslation
    ):
        self.illusts = illusts
        self.name = name
        self.translation = translation


class IllustSeries:
    def __init__(self, d: dict):
        self.id: int = int(d["id"])
        self.user_id: int = int(d["userId"])
        self.title: str = d["title"]
        self.description: str = d["description"]
        self.thumb_raw: Optional[str] = d["url"]
        self.thumb: Optional[str] = proxy(self.thumb_raw)
        self.thumb_sensitivity_level: int = d["coverImageSl"]
        self.thumb_is_sensitive: bool = self.thumb_sensitivity_level >= 4
        self.first_illust_id: int = int(d["firstIllustId"])
        self.latest_illust_id: int = int(d["latestIllustId"])
        self.create_date: datetime = datetime.fromisoformat(d["createDate"])
        self.update_date: datetime = datetime.fromisoformat(d["updateDate"])
        self.watch_count: Optional[int] = (
            int(d["watchCount"]) if d["watchCount"] else None
        )
        self.watched: bool = d["isWatched"]
        self.notifying: bool = d["isNotifying"]
