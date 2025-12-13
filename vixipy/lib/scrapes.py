from __future__ import annotations

import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
from typing import TYPE_CHECKING

from ..api.handler import pixiv_request
from ..converters import proxy

if TYPE_CHECKING:
    from bs4.element import Tag
    from typing import Optional

log = logging.getLogger("vixipy.lib.scrapes")


class CalendarEntry:
    def __init__(self, active, date, img, args, locked):
        self.active: bool = active
        self.img: Optional[str] = img
        self.args: Optional[dict] = args
        self.locked: bool = locked
        self.date: Optional[int] = int(date)

    def __repr__(self):
        return (
            "<CalendarEntry "
            f"active={self.active} "
            f"date={self.date} "
            f"img={self.img} "
            f"args={self.args} "
            f"locked={self.locked}>"
        )


class PopularTag:
    def __init__(self, name, link, count):
        self.name = name
        self.link = link
        self.count = int(count)


def parse_ranking_calendar(response: str) -> list[CalendarEntry]:
    s = BeautifulSoup(response, "html.parser")

    #  can't you fucking learn basic spelling, pixiv?
    main: Tag = s.find("table", class_="calender_ranking")
    res: list[CalendarEntry] = []
    tds: list[Tag] = main.find_all("td")
    for x in tds:
        if x.attrs.get("class") and x.attrs["class"][0] == "active":
            __active = True
        else:
            __active = False

        if __img_elem := x.find("img"):
            __img_elem: Tag
            __img = __img_elem.attrs["data-src"]
        else:
            __img = None

        if __date_elem := x.find("span", class_="date"):
            __date_elem: Tag
            __date = __date_elem.text
        else:
            __date = 0

        __locked = True if x.find("svg") else False

        if __url_elem := x.find("a"):
            __url_elem: Tag

            #  don't ask.
            __args = {
                y[0]: y[1]
                for y in [
                    z.split("=")
                    for z in __url_elem.attrs["href"].split("?")[1].split("&")
                ]
            }
        else:
            __args = None

        """
            log.debug(
                "Ranking calendar: active=%s, day=%s, date=%s, img=%s, args=%s",
                __active,
                __day,
                __date,
                __img,
                __args,
            )
            """
        res.append(CalendarEntry(__active, __date, __img, __args, __locked))
    return res


async def get_ranking_calendar(
    date: int = None, mode: str = "daily"
) -> list[CalendarEntry]:
    d = await pixiv_request(
        "/ranking_log.php", expect_json=False, params=[("mode", mode), ("date", date)]
    )

    start = time.perf_counter()
    res: list[CalendarEntry] = await asyncio.get_running_loop().run_in_executor(
        None, parse_ranking_calendar, d
    )
    end = time.perf_counter()

    log.debug("Ranking calendar: parse took %dms", (end - start) * 1000)

    #  do some post processing
    for w in res:
        if img := w.img:
            w.img = proxy(img)
    log.debug(res)
    return res


def parse_tags_page(response: str):
    s = BeautifulSoup(response, "html.parser")
    res: list[PopularTag] = []
    __links: list[Tag] = s.find_all("a", class_="tag-item")

    for x in __links:
        __name = x.find("div", class_="tag").text
        __link = x.attrs["href"].removeprefix("/en")
        __count = x.find("div", class_="count").text

        res.append(PopularTag(__name, __link, __count))
    return res


async def get_popular_tags(novel=False):
    params = [("type", "novel")] if novel else []
    res = await pixiv_request(
        "/tags", expect_json=False, touch=True, params=params, ignore_language=True
    )
    data: list[PopularTag] = await asyncio.get_running_loop().run_in_executor(
        None, parse_tags_page, res
    )
    return data
