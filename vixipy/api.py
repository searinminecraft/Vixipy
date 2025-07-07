from __future__ import annotations

from quart import current_app, g, request
import logging
import time
from typing import TYPE_CHECKING, List, Tuple
from urllib.parse import quote
from aiohttp import MultipartWriter
from aiohttp.client_exceptions import ContentTypeError, ServerDisconnectedError
import json
import random
import hashlib

from .filters import filter_from_prefs as ff
from .types import *

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from typing import Any

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
    json_payload: dict = None,
    raw_payload=None,
    touch=False,
    ignore_cache=False,
):
    ignore_cache = method == "post" or ignore_cache == True
    cache_enabled = current_app.config["CACHE_PIXIV_REQUESTS"]

    _cookies = {**cookies}
    _headers = {**headers}
    _params = ""
    cookie_header = ""

    try:
        lang = request.cookies.get("Vixipy-Language")
    except Exception:
        lang = "en"

    params = params.copy()

    params.append(("lang", {"en": "en", "ja": "ja", "zh_Hans": "zh"}.get(lang, "en")))

    for i, v in enumerate(params):
        if i == 0:
            _params += f"?{v[0]}={v[1]}"
        else:
            _params += f"&{v[0]}={v[1]}"

    hashed_value = hashlib.md5(bytes(endpoint + _params, "utf-8")).hexdigest()

    if cache_enabled and not ignore_cache:
        cache_result = await current_app.cache_client.get(
            bytes(f"endpoint_{hashed_value}", "utf-8")
        )
        if cache_result:
            log.info("[hit] %s", endpoint)
            return json.loads(cache_result)

    if touch or endpoint.startswith("/touch/ajax"):
        _headers["User-Agent"] = (
            "Mozilla/5.0 (Android 10; Mobile; rv:138.0) Gecko/138.0 Firefox/138.0"
        )

    if raw_payload and not isinstance(raw_payload, MultipartWriter):
        log.debug("Use urlencoded by default")
        _headers["Content-Type"] = "application/x-www-form-urlencoded"

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

    log.info("[%s] %s%s", method, endpoint, _params)

    req_start = time.perf_counter()
    while True:
        try:
            if current_app.config["PIXIV_DIRECT_CONNECTION"]:
                r: ClientResponse = await current_app.pixiv.request(
                    method,
                    endpoint + _params,
                    server_hostname="www.pixiv.net",
                    headers=_headers,
                    data=raw_payload,
                    json=json_payload,
                )
            else:
                r: ClientResponse = await current_app.pixiv.request(
                    method,
                    endpoint + _params,
                    headers=_headers,
                    data=raw_payload,
                    json=json_payload,
                )
        except ServerDisconnectedError:
            log.error("[%s] Got ServerDisconnectedError, trying again...", endpoint)
            continue
        else:
            break
    req_end = time.perf_counter()
    req_time = (req_end - req_start) * 1000

    if req_time >= 500:
        log.warning("[%s] Request took %dms", endpoint, req_time)
    log.info("[%dms] [%s] %d", req_time, endpoint, r.status)

    try:
        res = await r.json()
        if res.get("error") == True or res.get("isSucceed") == False:
            log.error("Error: pixiv API returned error %s", res["message"])
            raise PixivError(res["message"], r.status, endpoint)

        if res.get("body"):
            res = res["body"]
    except ContentTypeError:
        raise PixivError(await r.text(), r.status, endpoint)

    if cache_enabled and not ignore_cache:
        await current_app.cache_client.set(
            bytes(f"endpoint_{hashed_value}", "utf-8"),
            bytes(json.dumps(res), "utf-8"),
            int(current_app.config["CACHE_TTL"]),
        )

    return res


# ==========================================================
# // API CALLS                                            //
# ==========================================================


async def get_user(id: int, full: bool = False) -> User:
    data = await pixiv_request(f"/ajax/user/{id}", params=[("full", int(full))])
    if full:
        return User(data)
    else:
        return PartialUser(data)


async def get_user_profile_top(id: int) -> list[ArtworkEntry]:
    data = await pixiv_request(f"/ajax/user/{id}/profile/top")
    illusts = [ArtworkEntry(data["illusts"][x]) for x in data["illusts"]]
    manga = [ArtworkEntry(data["manga"][x]) for x in data["manga"]]
    return sorted(illusts + manga, key=lambda _: _.id, reverse=True)


async def get_user_illusts(
    id: int, content_type: str = "illust", page: int = 1, tag: str = None
):
    params = [("id", id), ("type", content_type), ("p", page)]

    if tag:
        params.append(("tag", tag))

    data = await pixiv_request("/touch/ajax/user/illusts", params=params)

    return UserPageIllusts(data)


async def get_user_bookmarks(
    id: int, page: int = 1, tag: str = ""
) -> tuple[int, list[ArtworkEntry]]:
    data = await pixiv_request(
        f"/ajax/user/{id}/illusts/bookmarks",
        params=[
            ("tag", tag),
            ("offset", (48 * page) - 48),
            ("limit", 48),
            ("rest", "show"),
        ],
    )
    return data["total"], [ArtworkEntry(x) for x in data["works"]]


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
        _pages.append(ArtworkPage(page, k + 1))
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
    for k, v in kwargs.items():
        _params.append((k, v))

    data = await pixiv_request(
        f"/ajax/search/{type_}/{quote(query, safe='')}", params=_params
    )
    match type_:
        case "top":
            return SearchResultsTop(data)
        case "illustrations":
            return SearchResultsIllust(data)
        case "manga":
            return SearchResultsManga(data)
        case "novels":
            return SearchResultsNovel(data)
        case _:
            raise ValueError("Invalid search type")


async def get_tag_info(tag: str):
    data = await pixiv_request(f"/ajax/search/tags/{quote(tag, safe='')}")
    return TagInfo(data)


async def get_ranking(mode: str = "daily", date: str = None, content: str = None):

    params = [("format", "json"), ("mode", mode)]

    if date:
        params.append(("date", date))
    if content:
        params.append(("content", content))

    data = await pixiv_request(f"/ranking.php", params=params)

    return RankingData(data)


async def get_discovery(
    mode: str = "all",
) -> list[ArtworkEntry]:

    data = await pixiv_request(
        "/ajax/discovery/artworks",
        params=[("mode", mode), ("limit", 100)],
        ignore_cache=True,
    )

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]


async def get_recommended_users() -> list[RecommendedUser]:
    data = await pixiv_request(
        "/ajax/discovery/users", params=[("limit", 50)], ignore_cache=True
    )

    _illusts_to_dict: dict[int, ArtworkEntry] = {
        int(x["id"]): ArtworkEntry(x) for x in data["thumbnails"]["illust"]
    }
    _users_to_dict: dict[int, PartialUser] = {
        int(x["userId"]): PartialUser(x) for x in data["users"]
    }

    result: list[RecommendedUser] = []

    for x in data["recommendedUsers"]:
        user = _users_to_dict[int(x["userId"])]
        illusts = [_illusts_to_dict[int(y)] for y in x["recentIllustIds"]]
        result.append(RecommendedUser(user, ff(illusts)))

    return result


async def get_novel(id: int) -> Novel:
    data = await pixiv_request(f"/ajax/novel/{id}")
    return Novel(data)


async def get_recommended_novels(id: int) -> list[NovelEntry]:
    data = await pixiv_request(
        f"/ajax/novel/{id}/recommend/init", params=[("limit", 20)]
    )
    return [NovelEntry(x) for x in data["novels"]]


async def get_novel_series(id: int) -> NovelSeries:
    data = await pixiv_request(f"/ajax/novel/series/{id}")
    return NovelSeries(data)


async def get_novel_series_contents(id: int, page: int = 1) -> NovelEntry:
    data = await pixiv_request(
        f"/ajax/novel/series_content/{id}",
        params=[("limit", 30), ("last_order", (30 * page) - 30), ("order_by", "asc")],
    )

    __entries: dict[int, NovelEntry] = {
        x["id"]: NovelEntry(x) for x in data["thumbnails"]["novel"]
    }

    for x in data["page"]["seriesContents"]:
        __entries[x["id"]].title = f"#{x['series']['contentOrder']} {x['title']}"

    return list(__entries.values())


async def get_artwork_comments(id: int, page: int = 1):
    data = await pixiv_request(
        "/ajax/illusts/comments/roots",
        params=[("illust_id", id), ("offset", (10 * page) - 10), ("limit", 10)],
        ignore_cache=True,
    )

    return CommentBaseResponse([Comment(x) for x in data["comments"]], data["hasNext"])


async def get_artwork_replies(id: int, page: int = 1):
    data = await pixiv_request(
        "/ajax/illusts/comments/replies",
        params=[("comment_id", id), ("page", page)],
        ignore_cache=True,
    )

    return CommentBaseResponse(
        [CommentBase(x) for x in data["comments"]], data["hasNext"]
    )
