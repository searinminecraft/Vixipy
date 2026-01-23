from __future__ import annotations

from ..converters import proxy, convert_pixiv_link
from datetime import datetime
import logging
from quart import render_template
from typing import Optional


log = logging.getLogger(__name__)


class _StreetAccessRms:
    def __init__(self, d: dict):
        self.scr: float = d["scr"]
        self.mtd: list[str] = d["mtd"]
        self.pos: int = d["pos"]
        self.sii: list = d["sii"]
        self.sni: list = d["sni"]
        self.rli: Optional[str] = d.get("rli")


class StreetAccessData:
    def __init__(self, d: dict):
        self.key: str = d["key"]
        self.typ: str = d["typ"]
        self.cid: int = d["cid"]
        self.i: int = d["i"]
        self.t: int = d["t"]
        self.ism: int = d["ism"]
        self.aui: Optional[int] = d.get("aui")
        self.tgs: Optional[list[str]] = d.get("tgs")
        self.rms: Optional[_StreetAccessRms] = _StreetAccessRms(d["rms"]) if d.get("rms") else None


class StreetNextParams:
    def __init__(self, d: dict):
        self.page: int = d["page"]
        self.content_index_prev: int = d["content_index_prev"]
        self.li: Optional[list[int]] = [int(x) for x in d["li"].split(",")] if d["li"] else None
        self.li: Optional[list[int]] = [int(x) for x in d["lm"].split(",")] if d["lm"] else None
        self.ln: Optional[list[int]] = [int(x) for x in d["ln"].split(",")] if d["ln"] else None
        self.lc: Optional[list[int]] = int(d["lc"] or 0) or None


class StreetComponent:
    def __init__(self, d: dict):
        self.name = d["kind"]
        self.access: Optional[StreetAccessData] = StreetAccessData(d["access"]) if d.get("access") else None

    async def render(self):
        return await render_template(f"street/components/{self.name}.html", data=self)


class _StreetPixivisionEntry:
    def __init__(self, d: dict):
        self.category: str = d["subCategory"]
        self.category_label: str = d["subCategoryLabel"]
        self.title: str = d["title"]
        self.url: str = convert_pixiv_link(d["url"])
        self.image: str = proxy(d["imageUrl"])


class StreetPixivisionComponent(StreetComponent):
    def __init__(self, d: dict):
        super().__init__(d)
        self.entries: list[_StreetPixivisionEntry] = [_StreetPixivisionCategory(x) for x in d["thumbnails"]]


class _StreetTag:
    def __init__(self, d: dict):
        self.name: str = d["name"]
        self.translated: Optional[str] = d["translatedName"]
        self.emphasized: bool = d["isEmphasized"]


class _StreetThumbCommon:
    def __init__(self, d: dict):
        self.id: int = int(d["id"])
        self.title: str = d["title"]
        self.tags: list[_StreetTag] = [_StreetTag(x) for x in d["tags"]]
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.profile_img: str = proxy(d["profileImageUrl"])
        self.create_date: datetime = datetime.strptime(d["createDate"], "%Y-%m-%d %H:%M:%S")
        self.update_date: datetime = datetime.strptime(d["createDate"], "%Y-%m-%d %H:%M:%S")
        self.comments_off: bool = bool(d["commentOffSetting"])
        self.ai: bool = d["aiType"] == 2
        self.bookmarkable: bool = d["bookmarkable"]
        self.show_tags: bool = d["showTags"]


class _StreetPickup:
    def __init__(self, d: dict):
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.comment_id: int = d["commentId"]
        self.comment: str = d["comment"]
        self.comment_count: int = d["commentCount"]

class _StreetImageUrls:
    def __init__(self, d: dict):
        self.standard = proxy(d["1200x1200_standard"])
        self.medium = proxy(d["540x540"])
        self.small = proxy(d["360x360"])


class _StreetImagePage:
    def __init__(self, d: dict):
        self.width: int = d["width"]
        self.height: int = d["height"]
        self.urls: _StreetImageUrls = _StreetImageUrls(d["urls"])


class _StreetIllustThumb(_StreetThumbCommon):
    def __init__(self, d: dict):
        super().__init__(d)
        self.page_count: int = d["pageCount"]
        self.pages: list[_StreetImagePage] = [_StreetImagePage(x) for x in d["pages"]]


class StreetIllust(StreetComponent):
    def __init__(self, d: dict):
        super().__init__(d)
        self.content: _StreetIllustThumb = _StreetIllustThumb(d["thumbnails"][0])
        self.pickup: Optional[_StreetPickup] = _StreetPickup(d["pickup"]) if d.get("pickup") else None


class _StreetNovelThumb(_StreetThumbCommon):
    def __init__(self, d: dict):
        super().__init__(d)
        self.description: str = d["description"]
        self.episode_count: int = d["episodeCount"]
        self.text: str = d["text"]
        self.thumb: str = proxy(d["url"])
        self.text_count: int = d["textCount"]
        self.word_count: int = d["wordCount"]
        self.use_word_count: bool = d["useWordCount"]
        self.reading_time: int = d["readingTime"]
        self.bookmark_count: int = d["bookmarkCount"]
        self.series_id: Optional[int] = int(d.get("seriesId", 0)) or None
        self.series_title: Optional[str] = d.get("seriesTitle")


class StreetNovel(StreetComponent):
    def __init__(self, d: dict):
        super().__init__(d)
        self.content: _StreetNovelThumb = _StreetNovelThumb(d["thumbnails"][0])


class _StreetCollectionThumb(_StreetThumbCommon):
    def __init__(self, d: dict):
        super().__init__(d)
        self.url: str = proxy(d["url"])
        self.language: str = d["language"]
        self.spoiler: bool = d["isSpoiler"]


class StreetCollection(StreetComponent):
    def __init__(self, d: dict):
        super().__init__(d)
        self.content: _StreetCollectionThumb = _StreetCollectionThumb(d["thumbnails"][0])




class StreetPlaceholderComponent(StreetComponent):
    def __init__(self, d):
        super().__init__(d)

    async def render(self):
        log.warn("Rendered placeholder!")
        return ""


class StreetData:
    def __init__(self, d: dict):
        self.contents: list[StreetComponent] = []
        self.next_params: StreetNextParams = StreetNextParams(d["nextParams"])

        _cmp_map = {
            "pixivision": StreetPixivisionComponent,
            "illust": StreetIllust,
            "manga": StreetIllust,
            "novel": StreetNovel,
            "collection": StreetCollection,
        }

        for x in d["contents"]:
            if x["kind"] in _cmp_map:
                n = _cmp_map[x["kind"]](x)
                self.contents.append(n)
                log.debug("Parsed street cmp %s", n.name)
            else:
                self.contents.append(StreetPlaceholderComponent(x))
                log.warn("Street cmp %s not implemented", x["kind"])

        self.k: str = self.contents[-1].name
