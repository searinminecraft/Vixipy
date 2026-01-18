from __future__ import annotations

from ..converters import proxy
from datetime import datetime
from typing import Optional


class CollectionEntry:
    def __init__(self, d):
        self.id: int = int(d["id"])
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.title: str = d["title"]
        self.tags: list[str] = d["tags"]
        self.alt: Optional[str] = d["caption"] or None
        self.language: str = d["language"]
        self.sl: int = d["sl"]
        self.sensitive: bool = self.sl >= 4
        self.xrestrict: int = d["xRestrict"]
        self.bookmark_count: int = d["bookmarkCount"]
        self.is_bookmarked: bool = d["bookmarkData"] is not None
        self.comment_off: bool = d["commentOff"]
        self.spoiler: bool = d["isSpoiler"]
        self.bookmarkable: bool = d["isBookmarkable"]
        self.view_count: int = d["viewCount"]
        self.cited_data_hash: str = d["citedDataHash"]
        self.status: str = d["status"]
        self.published: datetime = (
            datetime.strptime(d["publishedDateTime"], "%Y-%m-%d %H:%M:%S"),
        )
        self.thumb = proxy(d["thumbnailImageUrl"] + "?format=png")

    def __repr__(self):
        return f"<CollectionEntry title={self.title} id={self.id} user_id={self.user_id} user_name={self.user_name}>"
