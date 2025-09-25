from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .components import PixivisionComponent


class PixivisionCategory(Enum):
    ILLUSTRATION = "illustration"
    MANGA = "manga"
    NOVELS = "novels"
    COSPLAY = "cosplay"
    MUSIC = "music"
    GOODS = "goods"
    HOW_TO_DRAW = "how-to-draw"
    DRAW_STEP_BY_STEP = "draw-step-by-step"
    TEXTURES = "textures"
    ART_REFERENCES = "art-references"
    HOW_TO_MAKE = "how-to-make"
    RECOMMEND = "recommend"
    INTERVIEW = "interview"
    COLUMN = "column"
    NEWS = "news"
    DESKWATCH = "deskwatch"
    TRY_OUT = "try-out"


class PixivisionTag:
    def __init__(
        self,
        id: int,
        name: str,
    ):
        self.id: int = id
        self.name: str = name


class PixivisionEntry:
    def __init__(
        self,
        id: int,
        title: str,
        date: datetime,
        image: str,
        category: str,
        tags: list[PixivisionTag],
    ):
        self.id: int = id
        self.title: str = title
        self.date: datetime = date
        self.image: str = image
        self.category: PixivisionCategory = PixivisionCategory(category)
        self.tags: list[PixivisionTag] = tags


class PixivisionArticle:
    def __init__(
        self,
        title: str,
        category: str,
        date: datetime,
        contents: list[PixivisionComponent],
        og_desc: str,
        og_img: str,
    ):
        self.title: str = title
        self.category: PixivisionCategory = PixivisionCategory(category)
        self.date: datetime = date
        self.contents: list[PixivisionComponent] = contents
        self.og_desc: str = og_desc
        self.og_img: str = og_img


class PixivisionLanding:
    def __init__(
        self,
        spotlight: Optional[PixivisionEntry],
        articles: list[PixivisionEntry],
        page_caps: tuple[bool, bool],
    ):
        self.spotlight: Optional[PixivisionEntry] = spotlight
        self.articles: list[PixivisionEntry] = articles
        self.page_caps: tuple[bool, bool] = page_caps
