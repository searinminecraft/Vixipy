from __future__ import annotations

from .common import TagTranslation, Tag
from ..converters import proxy

from .artworks import ArtworkEntry
from .novels import NovelEntry

from typing import Optional


class SearchResultsBase:
    def __init__(
        self,
        d,
    ):
        _related_tags = d["relatedTags"]
        _tag_translation = d["tagTranslation"]
        if isinstance(_tag_translation, list):
            self.related_tags = [Tag(x, None) for x in _related_tags]
        else:
            if isinstance(_related_tags, list):
                self.related_tags = _related_tags
            else:
                self.related_tags = [
                    Tag(x, _tag_translation.get(x, {"en": None})["en"])
                    for x in _related_tags
                ]


class SearchResultsTop(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total_novel: int = d["novel"]["total"]
        self.novels: list[NovelEntry] = [NovelEntry(x) for x in d["novel"]["data"]]
        if im := d.get("illustManga"):
            self.total_illustmanga: int = d["illustManga"]["total"]
            self.total: int = self.total_illustmanga + d["novel"]["total"]
            self.results: list[ArtworkEntry] = [
                ArtworkEntry(x) for x in d["illustManga"]["data"]
            ]
        else:
            _illusts = d["illust"]
            _manga = d["manga"]

            self.total_illustmanga: int = _illusts["total"] + _manga["total"]
            self.total = self.total_illustmanga + d["novel"]["total"]
            self.results: list[ArtworkEntry] = sorted(
                [ArtworkEntry(x) for x in _illusts["data"]]
                + [ArtworkEntry(x) for x in _manga["data"]],
                key=lambda _: _.id,
                reverse=True,
            )

        _popular = d["popular"]
        self.popular_recent = [ArtworkEntry(x) for x in _popular["recent"]]
        self.popular_permanent = [ArtworkEntry(x) for x in _popular["permanent"]]


class SearchResultsIllust(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["illust"]["total"]
        self.last: int = d["illust"]["lastPage"]
        self.results: list[ArtworkEntry] = []

        for x in d["illust"]["data"]:
            if x.get("isAdContainer"):
                continue
            self.results.append(ArtworkEntry(x))


class SearchResultsManga(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["manga"]["total"]
        self.last: int = d["manga"]["lastPage"]
        self.results: list[ArtworkEntry] = []

        for x in d["manga"]["data"]:
            if x.get("isAdContainer"):
                continue
            self.results.append(ArtworkEntry(x))


class SearchResultsNovel(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["novel"]["total"]
        self.results: list[NovelEntry] = [NovelEntry(x) for x in d["novel"]["data"]]
        self.last: int = d["novel"]["lastPage"]


class PixpediaInfo:
    def __init__(self, d):
        self.abstract: Optional[str] = d.get("abstract")
        self.image: Optional[str] = proxy(d.get("image"))


class TagInfo:
    def __init__(self, d):
        self.tag = d["tag"]
        self.pixpedia: PixpediaInfo = PixpediaInfo(d["pixpedia"])
        self.translation: Optional[TagTranslation] = None
        self.favorite_tags: list[str] = d["myFavoriteTags"]
        self.is_favorite: bool = self.tag in self.favorite_tags
        if self.tag in d["tagTranslation"]:
            self.translation = TagTranslation(self.tag, d["tagTranslation"][self.tag])
