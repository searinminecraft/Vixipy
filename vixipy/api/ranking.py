from __future__ import annotations

from typing import Union

from .handler import pixiv_request
from ..types import RankingData, RankingCalendar

MODES_T = Union[
    "daily",
    "weekly",
    "monthly",
    "rookie",
    "male",
    "female",
    "original",
    "daily_ai",
    "daily_r18_ai",
    "daily_r18",
    "weekly_r18",
    "male_r18",
    "female_r18",
    "r18g",
]

VALID_MODES = (
    "daily",
    "weekly",
    "monthly",
    "rookie",
    "male",
    "female",
    "original",
    "daily_ai",
    "daily_r18_ai",
    "daily_r18",
    "weekly_r18",
    "male_r18",
    "female_r18",
    "r18g",
)


async def get_ranking(
    mode: MODES_T = "daily", date: str = None, content: str = None, page: int = 1
):

    if mode not in VALID_MODES:
        raise ValueError("Invalid mode, must be one of: %s" % (", ".join(VALID_MODES),))

    params = [("format", "json"), ("mode", mode), ("p", page)]

    if date:
        params.append(("date", date))
    if content:
        params.append(("content", content))

    data = await pixiv_request(f"/ranking.php", params=params)

    return RankingData(data)


async def get_ranking_calendar(mode: MODES_T = None, date: str = None):

    if mode not in VALID_MODES:
        raise ValueError("Invalid mode, must be one of: %s" % (", ".join(VALID_MODES),))

    params = []

    if mode:
        params.append(("mode", mode))
    if date:
        params.append(("date", date))

    data = await pixiv_request("/ajax/ranking_log", params=params, ignore_language=True)
    return RankingCalendar(data)
