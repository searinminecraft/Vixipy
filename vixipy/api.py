from __future__ import annotations

from quart import current_app, g
import logging
import time
from typing import TYPE_CHECKING, List, Tuple

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

        if method.lower() == "post":
            _headers["x-csrf-token"] = g.csrf
    else:
        _cookies["p_ab_d_id"] = current_app.pixiv_p_ab_d_id
        _cookies["p_ab_d_id"] = current_app.pixiv_p_ab_id
        _cookies["p_ab_d_id"] = current_app.pixiv_p_ab_id_2
        if not "PHPSESSID" in _cookies:
            if current_app.config.get("TOKEN"):
                _cookies["PHPSESSID"] = current_app.config["TOKEN"]
            else:
                _cookies["PHPSESSID"] = current_app.pixiv_phpsessid

    for k, v in _cookies.items():
        cookie_header += f"{k}={v}; "

    _headers["Cookie"] = cookie_header

    log.info("Requesting %s with method %s", endpoint, method)

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
    
    res = await r.json()
    if res.get("error") == True or res.get("isSucceed") == False:
        raise PixivError(res["message"], r.status, endpoint)

    if res.get('body'):
        return res["body"]
    else:
        return res
            

async def get_user(id: int, full: bool = False) -> User:
    data = await pixiv_request(f"/ajax/user/{id}", params=[("full", int(full))])
    if full:
        return User(data)
    else:
        return PartialUser(data)    

async def get_notification_count() -> int:
    data = await pixiv_request(f"/rpc/notify_count.php", params=[("op", "count_unread")], headers={"Referer": "https://www.pixiv.net"})
    return data["popboard"]

async def get_self_extra() -> UserExtraData:
    data = await pixiv_request("/ajax/user/extra")
    return UserExtraData(data)


async def get_artwork(id: int) -> Artwork:
    data = await pixiv_request(f"/ajax/illust/{id}")
    return Artwork(data)

async def get_artwork_pages(id: int) -> ArtworkPage:
    data = await pixiv_request(f"/ajax/illust/{id}/pages")
    return [ArtworkPage(x) for x in data]

async def get_recommended_works(id: int) -> list[ArtworkEntry]:
    data = await pixiv_request(f"/ajax/illust/{id}/recommend/init", params=[('limit', '180')])
    return [ArtworkEntry(x) for x in data["illusts"]]