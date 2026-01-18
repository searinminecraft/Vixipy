from __future__ import annotations

from .artworks import ArtworkEntry
from ..converters import proxy
from datetime import datetime
from enum import Enum

from typing import Optional


class RankingEntry(ArtworkEntry):
    def __init__(self, d):
        _cd = datetime.strptime(d["date"], "%Y年%m月%d日 %H:%M")
        super().__init__(
            {
                "id": d["illust_id"],
                "title": d["title"],
                "description": None,
                "illustType": d["illust_type"],
                "createDate": _cd.isoformat(),
                "xRestrict": 0,
                "sl": 2,
                "alt": "",
                "userId": d["user_id"],
                "userName": d["user_name"],
                "pageCount": d["illust_page_count"],
                "aiType": 0,
                "url": d["url"],
                "profileImageUrl": d["profile_img"],
                "bookmarkData": (
                    {
                        "id": int(d["bookmark_id"]),
                        "private": int(d["bookmark_illust_restrict"]) == 1,
                    }
                    if d.get("is_bookmarked")
                    else None
                ),
                "tags": "",
            }
        )
        self.rank: int = int(d["rank"])


class RankingData:
    def __init__(self, d):
        self.page: int = d["page"]
        self.prev: Optional[int] = d["prev"] if d["prev"] != False else None
        self.next: Optional[int] = d["next"] if d["next"] != False else None
        self.date_r: str = d["date"]
        self.date: datetime = datetime.strptime(self.date_r, "%Y%m%d")
        self.prev_date_r: Optional[str] = (
            d["prev_date"] if d["prev_date"] != False else None
        )
        self.prev_date: Optional[datetime] = (
            datetime.strptime(self.prev_date_r, "%Y%m%d") if self.prev_date_r else None
        )
        self.next_date_r: Optional[str] = (
            d["next_date"] if d["next_date"] != False else None
        )
        self.next_date: Optional[datetime] = (
            datetime.strptime(self.next_date_r, "%Y%m%d") if self.next_date_r else None
        )
        self.mode: str = d["mode"]
        self.content: str = d["content"]
        self.contents: list[RankingEntry] = []

        for x in d["contents"]:
            self.contents.append(RankingEntry(x))


class MaskReason(Enum):
    R18 = "r18"
    R18G = "r18g"
    UNKNOWN = "unknown"
    SENSITIVITY_LEVEL = "sl"
    MYPIXIV = "mypixiv"
    MASKING = "masking"
    LOGIN_ONLY = "login_only"


class RankingCalendarEntry:
    def __init__(self, d: dict):
        self.day_str: str = d["day"]
        self.day: int = int(self.day_str)
        self.week: str = d["week"]
        self.img: Optional[str] = proxy(d.get("img"))
        self.user_id: Optional[int] = int(d["user_id"]) if d.get("user_id") else None
        self.tags: Optional[list[str]] = d["tags"] if d.get("tags") else None
        self.is_masked: bool = d.get("is_masked") or False
        self.mask_reason: Optional[MaskReason] = (
            MaskReason(d["mask_reason"]) if d.get("mask_reason") else None
        )


class RankingCalendar:
    def __init__(self, d: dict):
        d = d["display_a"]
        self.mode: str = d["mode"]
        self.content: str = d["content"]
        self.date: str = d["date"]
        self.current_year: int = int(d["now_year"])
        self.current_month: int = int(d["now_month"])
        self.max_year: int = int(d["max_year"])
        self.max_month: int = int(d["max_month"])
        self.calendar = [RankingCalendarEntry(x) for x in d["calendar"]]
