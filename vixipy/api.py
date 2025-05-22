from __future__ import annotations

from quart import current_app, g
import logging
import time
from typing import TYPE_CHECKING, List, Tuple
from urllib.parse import quote
from aiohttp.client_exceptions import ContentTypeError
import random

from .types import *

if TYPE_CHECKING:
    from aiohttp import ClientResponse

log = logging.getLogger("vixipy.api")


class PixivError(Exception):
    def __init__(self, message: str, code: int, path: str):
        self.code: int = code
        self.path: str = path
        self.message: str = message

        super().__init__(f"{code}: {message} - {path}")


async def pixiv_request(
    endpoint: str,
    method: str = "get",
    params: List[Tuple[str, str]] = [],
    *,
    cookies={},
    headers: dict = {},
    json_payload: dict = {},
    raw_payload=None,
):

    _cookies = {**cookies}
    _headers = {**headers}
    _params = ""
    cookie_header = ""

    for i, v in enumerate(params):
        if i == 0:
            _params += f"?{v[0]}={v[1]}"
        else:
            _params += f"&{v[0]}={v[1]}"

    if g.authorized:
        _cookies["p_ab_d_id"] = g.p_ab_d_id
        _cookies["p_ab_id"] = g.p_ab_id
        _cookies["p_ab_id_2"] = g.p_ab_id_2
        _cookies["PHPSESSID"] = g.token
        _cookies["yuid_b"] = g.yuid_b

        if method.lower() == "post":
            _headers["x-csrf-token"] = g.csrf
    else:
        if not g.get("chosen_token", None):
            g.chosen_token = random.choice(current_app.tokens)
        log.debug("Using %s", g.chosen_token)
        _cookies["p_ab_d_id"] = g.chosen_token["p_ab_d_id"]
        _cookies["p_ab_id"] = g.chosen_token["p_ab_id"]
        _cookies["p_ab_id_2"] = g.chosen_token["p_ab_id_2"]
        _cookies["yuid_b"] = g.chosen_token["yuid_b"]
        if not "PHPSESSID" in _cookies:
            _cookies["PHPSESSID"] = g.chosen_token["token"]

    for k, v in _cookies.items():
        cookie_header += f"{k}={v}; "

    _headers["Cookie"] = cookie_header

    log.info("Requesting %s%s with method %s", endpoint, _params, method)

    req_start = time.perf_counter()
    r: ClientResponse = await current_app.pixiv.request(
        method,
        endpoint + _params,
        headers=_headers,
        data=raw_payload,
        json=json_payload,
    )
    req_end = time.perf_counter()
    log.info("%s status %d - %dms", endpoint, r.status, (req_end - req_start) * 1000)

    try:
        res = await r.json()
        if res.get("error") == True or res.get("isSucceed") == False:
            raise PixivError(res["message"], r.status, endpoint)

        if res.get("body"):
            return res["body"]
        else:
            return res
    except ContentTypeError:
        raise PixivError(await r.text(), r.status, endpoint)


# ==========================================================
# // API CALLS                                            //
# ==========================================================

async def get_user(id: int, full: bool = False) -> User:
    data = await pixiv_request(f"/ajax/user/{id}", params=[("full", int(full))])
    if full:
        return User(data)
    else:
        return PartialUser(data)


async def get_notification_count() -> int:
    data = await pixiv_request(
        f"/rpc/notify_count.php",
        params=[("op", "count_unread")],
        headers={"Referer": "https://www.pixiv.net"},
    )
    return data["popboard"]


async def get_self_extra() -> UserExtraData:
    data = await pixiv_request("/ajax/user/extra")
    return UserExtraData(data)


async def get_artwork(id: int) -> Artwork:
    data = await pixiv_request(f"/ajax/illust/{id}")
    return Artwork(data)


async def get_artwork_pages(id: int) -> list[ArtworkPage]:
    data = await pixiv_request(f"/ajax/illust/{id}/pages")
    _pages = []
    for k, page in enumerate(data):
        _pages.append(ArtworkPage(page, k+1))
    return _pages


async def get_recommended_works(id: int) -> list[ArtworkEntry]:
    data = await pixiv_request(
        f"/ajax/illust/{id}/recommend/init", params=[("limit", "180")]
    )
    return [ArtworkEntry(x) for x in data["illusts"]]


async def get_user_illusts_from_ids(user_id: int, ids: list[int]) -> list[ArtworkEntry]:
    if len(ids) == 0:
        return []

    data = await pixiv_request(
        f"/ajax/user/{user_id}/illusts", params=[("ids[]", x) for x in ids]
    )
    return [ArtworkEntry(x) for x in data.values()]

async def search(type_: str, query: str, **kwargs):
    _params = []
    for k,v in kwargs.items():
        _params.append((k,v))

    data = await pixiv_request(
        f"/ajax/search/{type_}/{quote(query, safe='')}", params=_params
    )
    match type_:
        case "top":
            return SearchResultsTop(data)
        case "artworks":
            return SearchResultsIllustManga(data)
        case "manga":
            return SearchResultsManga(data)
        case _:
            raise ValueError("Invalid search type")

async def get_tag_info(tag: str):
    data = await pixiv_request(f"/ajax/search/tags/{quote(tag, safe='')}")
    return TagInfo(data)


async def get_ranking(
    mode: str = "daily",
    date: str = None,
    content: str = None
):

    params = [
        ('format', 'json'),
        ('mode', mode)
    ]

    if date:
        params.append(('date', date))
    if content:
        params.append(('content', content))

    data = await pixiv_request(
        f"/ranking.php",
        params=params
    )

    return RankingData(data)

async def get_discovery(
    mode: str = "all",
) -> list[ArtworkEntry]:

    data = await pixiv_request("/ajax/discovery/artworks", params=[('mode', mode), ('limit', 100)])

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]