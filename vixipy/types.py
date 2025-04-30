from .converters import proxy
from datetime import datetime

from typing import Optional

NO_IMAGE = "https://s.pximg.net/common/images/no_profile.png"
NO_IMAGE_S = "https://s.pximg.net/common/images/no_profile_s.png"

def blank_to_none(v) -> Optional[str]:
    return v if v != "" else None


class PartialUser:
    def __init__(self, d):
        self.id = d["userId"]
        self.name = d["name"]
        self.image = proxy(d["image"])
        self.imageBig = proxy(d["imageBig"])
        self.premium = d["premium"]
        self.followed = d["isFollowed"]
        self.isMypixiv = d["isMypixiv"]
        self.blocked = d["isBlocking"]
        self.background = proxy(d["background"]["url"]) if d["background"] else None


class User(PartialUser):
    def __init__(self, d):
        super().__init__(d)
        self.following = d["following"]
        self.mypixiv = d["mypixivCount"]
        self.followedBack = d["followedBack"]
        self.comment = d["comment"]
        self.webpage = d["webpage"]
        self.official = d["official"]


class UserExtraData:
    def __init__(self, d):
        self.following = d["following"]
        self.followers = d["followers"]
        self.mypixivCount = d["mypixivCount"]
        self.background = proxy(d["background"]["url"]) if d["background"] else None


class Tag:
    def __init__(self, name, en=None, romaji=None):
        self.name = name
        self.en = en
        self.romaji = romaji


class ArtworkBase:
    def __init__(self, d):
        self.id = d["id"]
        self.title = d["title"]
        self.description = d["description"]
        self.type = d["illustType"]
        self.uploadDate = datetime.fromisoformat(d["createDate"])
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
    
    @property
    def xrestrict_friendlyname(self):
        names = {
            1: "R-18",
            2: "R-18G"
        }

        return names.get(int(self.xrestrict), "R-18")


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

        self.authorHandle = d["userAccount"]
        self.width = d["width"]
        self.height = d["height"]
        self.bookmarkCount = d["bookmarkCount"]
        self.likeCount = d["likeCount"]
        self.commentCount = d["commentCount"]
        self.viewCount = d["viewCount"]

        self.original = d["isOriginal"]
        self.loginonly = d["isLoginOnly"]
        self.ai = d["aiType"] == 2

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
        self.thumb = proxy(d["url"])
        self.profileimg = proxy(d.get("profileImageUrl"))
    
    def __repr__(self):
        return f"<ArtworkEntry {self.id}>"


class ArtworkPage:
    def __init__(self, d, page):
        self.reg = proxy(d["urls"]["regular"])
        self.orig = proxy(d["urls"]["original"])
        self.width = d["width"]
        self.height = d["height"]
        self.page = page


class TagTranslation:
    def __init__(self, orig: str, d):
        self.orig: str = orig
        self.en: Optional[str] = blank_to_none(d.get("en"))
        self.ja: Optional[str] = blank_to_none(d.get("ja"))
        self.ko: Optional[str] = blank_to_none(d.get("ko"))
        self.zh: Optional[str] = blank_to_none(d.get("zh"))
        self.zh_tw: Optional[str] = blank_to_none(d.get("zh_tw"))
        self.romaji: Optional[str] = blank_to_none(d.get("romaji"))


class RecommendByTag:
    def __init__(
        self, illusts: list[ArtworkEntry], name: str, translation: TagTranslation
    ):
        self.illusts = illusts
        self.name = name
        self.translation = translation

class SearchResultsBase:
    def __init__(
        self,
        d,
    ):
        _related_tags = d["relatedTags"]
        _tag_translation = d["tagTranslation"]
        self.related_tags = [Tag(x, _tag_translation.get(x, {"en": None})["en"]) for x in _related_tags]

class SearchResultsTop(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total_novel: int = d["novel"]["total"]
        if im := d.get("illustManga"):
            self.total_illustmanga: int = d["illustManga"]["total"]
            self.total: int = self.total_illustmanga + d["novel"]["total"]
            self.results: list[ArtworkEntry] = [ArtworkEntry(x) for x in d["illustManga"]["data"]]
        else:
            _illusts = d["illust"]
            _manga = d["manga"]

            self.total_illustmanga: int = _illusts["total"] + _manga["total"]
            self.total = self.total_illustmanga + d["novel"]["total"]
            self.results: list[ArtworkEntry] = sorted(
                [ArtworkEntry(x) for x in _illusts["data"]] +
                [ArtworkEntry(x) for x in _manga["data"]],
                key=lambda _: _.id,
                reverse=True
            )

class SearchResultsIllustManga(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["illustManga"]["total"]
        self.results: list[ArtworkEntry] = [ArtworkEntry(x) for x in d["illustManga"]["data"]]

class SearchResultsManga(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["manga"]["total"]
        self.results: list[ArtworkEntry] = [ArtworkEntry(x) for x in d["manga"]["data"]]

class PixpediaInfo:
    def __init__(self, d):
        self.abstract: Optional[str] = d.get("abstract")
        self.image: Optional[str] = proxy(d.get("image"))

class TagInfo:
    def __init__(self, d):
        self.tag = d["tag"]
        self.pixpedia: PixpediaInfo = PixpediaInfo(d["pixpedia"])
        self.translation: Optional[TagTranslation] = None
        if self.tag in d["tagTranslation"]:
            self.translation = TagTranslation(self.tag, d["tagTranslation"][self.tag])