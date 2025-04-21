from __future__ import annotations

from quart import current_app, g
import logging
import time
from typing import TYPE_CHECKING, Iterable, List, Tuple

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
    params: Iterable[List[Tuple]] = [],
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
        _cookies["p_ab_d_id"] = app.pixiv_p_ab_d_id
        _cookies["p_ab_d_id"] = app.pixiv_p_ab_id
        _cookies["p_ab_d_id"] = app.pixiv_p_ab_id_2
        if not "PHPSESSID" in _cookies:
            _cookies["PHPSESSID"] = app.pixiv_phpsessid

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
    return res