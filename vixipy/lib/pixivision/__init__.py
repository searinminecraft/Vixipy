from __future__ import annotations

from .parser import *
from ._types import *
from ...converters import proxy, convert_pixiv_link

import asyncio
from bs4 import BeautifulSoup
from http import HTTPStatus
import logging
from quart import abort, current_app, request
import time
from typing import TYPE_CHECKING, Callable


log = logging.getLogger("vixipy.lib.pixivision")


def get_preferred_language():
    mapping = {"en": "en", "ja": "ja", "ko": "ko", "zh_Hans": "zh", "zh_Hant": "zh-tw"}

    if l := request.args.get("lang"):
        if l not in mapping.values():
            abort(400)
        return l
    if c := request.cookies.get("Vixipy-Preferred-Pixivision-Language"):
        return c
    else:
        return mapping.get(request.cookies.get("Vixipy-Language"), "en")


async def _run_in_ex(func: Callable, *args):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args)


async def _pixivision_request(endpoint, params: dict[str, str] = {}) -> BeautifulSoup:
    language = get_preferred_language()

    start = time.perf_counter()

    r = await current_app.pixivision.get(
        f"/{language}{endpoint}",
        params=params,
        headers={"Cookie": f"user_lang={language.replace('-', '_')};"},
    )

    req_done = time.perf_counter()

    log.info(
        "[%dms] %s %s",
        (req_done - start) * 1000,
        endpoint,
        str(HTTPStatus(r.status)),
    )

    r.raise_for_status()
    data = await r.text()

    r.close()

    req_finish = time.perf_counter()

    log.info(
        "[%dms] [done] %s",
        (req_finish - start) * 1000,
        endpoint,
    )

    s = BeautifulSoup(data, "html.parser")

    for x in s.find_all("a"):
        x.attrs["href"] = convert_pixiv_link(x.attrs["href"])

    for x in s.find_all("img"):
        x.attrs["src"] = proxy(x.attrs["src"])

    for x in s.find_all("iframe"):
        x.attrs["src"] = convert_pixiv_link(x.attrs["src"])

    init_parse_finish = time.perf_counter()

    log.info(
        "[%dms] [parsed] %s",
        (init_parse_finish - start) * 1000,
        endpoint,
    )

    return s


async def get_landing_page(page: int = 1):
    d = await _pixivision_request("/", {"p": page})
    spotlight, articles, pg = await asyncio.gather(
        _run_in_ex(parse_spotlight, d),
        _run_in_ex(parse_article_entries, d),
        _run_in_ex(get_pagination_capabilities, d),
    )

    if spotlight:
        spotlight.image = proxy(spotlight.image)

    for x in articles:
        x.image = proxy(x.image)

    return PixivisionLanding(spotlight, articles, pg)


async def search(term: str, page: int = 1):
    d = await _pixivision_request("/s", {"q": term, "p": page})
    res, pg = await asyncio.gather(
        _run_in_ex(parse_article_entries, d),
        _run_in_ex(get_pagination_capabilities, d),
    )

    for x in res:
        x.image = proxy(x.image)

    return res, pg


async def get_article(id: int):
    d = await _pixivision_request(f"/a/{id}")
    res = await _run_in_ex(parse_article, d)
    return res


async def get_tag(id: int, page: int = 1):
    d = await _pixivision_request(f"/t/{id}", {"p": page})
    res, pg = await asyncio.gather(
        _run_in_ex(parse_article_entries, d),
        _run_in_ex(get_pagination_capabilities, d),
    )

    for x in res:
        x.image = proxy(x.image)

    return res, pg


async def get_category(id: int, page: int = 1):
    d = await _pixivision_request(f"/c/{id}", {"p": page})
    res, pg = await asyncio.gather(
        _run_in_ex(parse_article_entries, d),
        _run_in_ex(get_pagination_capabilities, d),
    )

    for x in res:
        x.image = proxy(x.image)

    return res, pg
