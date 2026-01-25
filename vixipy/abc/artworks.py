from __future__ import annotations

from .common import Tag
from ..converters import proxy
from datetime import datetime
import markupsafe
from typing import TYPE_CHECKING

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

        self.original = d["isOriginal"]
        self.loginonly = d["isLoginOnly"]
        self.ai = d["aiType"] == 2
        self.description = d["illustComment"]
        self.description_stripped = markupsafe.Markup(self.description).striptags()

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
