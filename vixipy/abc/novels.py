from __future__ import annotations

from ..converters import convert_pixiv_link, proxy
from datetime import datetime

from typing import Optional


class NovelBase:
    def __init__(self, d: dict):
        self.ai: int = d["aiType"] == 2
        self.bookmark_count: int = d["bookmarkCount"]
        self.create_date: datetime = datetime.fromisoformat(
            d.get("createDate") or d.get("createDateTime")
        )
        self.genre_id: int = int(d["genre"])
        self.id: int = int(d["id"])
        self.original: bool = d["isOriginal"]
        self.reading_time: int = d["readingTime"]
        self.tags: list[str] = d["tags"]
        self.title: str = d["title"]
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.word_count: int = d["wordCount"]
        self.character_count: int = int(
            d.get("characterCount") or d.get("textCount") or d.get("textLength")
        )
        self.xrestrict = d["xRestrict"]

    @property
    def xrestrict_friendlyname(self):
        names = {1: "R-18", 2: "R-18G"}

        return names.get(int(self.xrestrict), "R-18")


class NovelSeriesEntry(NovelBase):
    def __init__(self, d):
        super().__init__(d)
        self.cover: str = proxy(d["cover"]["urls"]["240mw"])
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.oneshot: bool = d["isOneshot"]
        self.caption: str = d["caption"]
        self.concluded: bool = d["isConcluded"]
        self.episode_count: int = d["episodeCount"]
        self.published_episode_count: int = d["publishedEpisodeCount"]
        self.latest_published_date: datetime = datetime.fromisoformat(
            d["latestPublishDateTime"]
        )
        self.latest_episode_id: int = int(d["latestEpisodeId"])
        self.watched: bool = d["isWatched"]
        self.notifying: bool = d["isNotifying"]
        self.published_character_count: int = d["publishedTextLength"]
        self.published_word_count: int = d["publishedWordCount"]
        self.published_reading_time: int = d["publishedReadingTime"]


class NovelSeries:
    def __init__(self, d):
        self.id: int = int(d["id"])
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.xrestrict: int = d["xRestrict"]
        self.original: bool = d["isOriginal"]
        self.concluded: bool = d["isConcluded"]
        self.genre_id: int = int(d["genreId"])
        self.title: str = d["title"]
        self.caption: str = d["caption"]
        self.language: str = d["language"]
        self.tags: list[str] = d["tags"]
        self.published_content_count: int = d["publishedContentCount"]
        self.published_character_count: int = d["publishedTotalCharacterCount"]
        self.published_word_count: int = d["publishedTotalWordCount"]
        self.published_reading_time: int = d["publishedReadingTime"]
        self.latest_published_date: datetime = datetime.fromtimestamp(
            d["lastPublishedContentTimestamp"]
        )
        self.created_date: datetime = datetime.fromtimestamp(d["createdTimestamp"])
        self.updated_date: datetime = datetime.fromtimestamp(d["updatedTimestamp"])
        self.first_novel_id: int = int(d["firstNovelId"])
        self.lastest_novel_id: int = int(d["latestNovelId"])
        self.total: int = d["total"]
        self.cover: str = proxy(d["cover"]["urls"]["480mw"])
        self.watched: bool = d["isWatched"]
        self.ai: bool = d["aiType"] == 2
        self.has_glossary: bool = d["hasGlossary"]


class NovelSeriesNav:
    def __init__(self, d):
        self.title: str = d["title"]
        self.order: int = d["order"]
        self.id: int = int(d["id"])
        self.available: bool = d["available"]


class NovelSeriesNavData:
    def __init__(self, d):
        self.series_id: int = d["seriesId"]
        self.title: str = d["title"]
        self.concluded: bool = d["isConcluded"]
        self.watched: bool = d["isWatched"]
        self.notifying: bool = d["isNotifying"]
        self.order: int = d["order"]
        self.prev: NovelSeriesNav = NovelSeriesNav(d["prev"]) if d["prev"] else None
        self.next: NovelSeriesNav = NovelSeriesNav(d["next"]) if d["next"] else None


class NovelEntry(NovelBase):
    def __init__(self, d):
        super().__init__(d)
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.description: str = d["description"]
        self.bookmarked = d["bookmarkData"] is not None
        self.cover = proxy(d["url"])


class Novel(NovelBase):
    def __init__(self, d):
        super().__init__(d)
        self.description: str = d["description"]
        self.view_count: int = d["viewCount"]
        self.bungei: bool = d["isBungei"]
        self.content: str = d["content"]
        self.cover: str = proxy(d["coverUrl"])
        self.bookmarked: bool = d["bookmarkData"] is not None
        self.liked: bool = d["likeData"]
        self.tags: list[str] = [x["tag"] for x in d["tags"]["tags"]]
        self.series_nav_data: Optional[NovelSeriesNavData] = (
            NovelSeriesNavData(d["seriesNavData"]) if d["seriesNavData"] else None
        )
        self.user_novels: list[NovelEntry] = []

        for x in d["userNovels"].values():
            if x is not None:
                self.user_novels.append(NovelEntry(x))

        self.comment_count: int = d["commentCount"]
        self.commentOff: bool = bool(d["commentOff"])
        self.language: str = d["language"]
