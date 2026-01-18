from __future__ import annotations

from quart import current_app, request, g

from aiohttp import MultipartWriter
from aiohttp.client_exceptions import ContentTypeError, ServerDisconnectedError
import hashlib
import json
import logging
import random
import time
from typing import List, Tuple
from urllib.parse import quote

from ..util import add_server_timing_metric

log = logging.getLogger(__name__)


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
    expect_json=True,
    ignore_language=False,
):
    """
    Send a request to pixiv

    Params:

    endpoint: endpoint to use
    method: method to use (default: get)
    params: parameters in a list[tuple[key, value]] format
    cookies: additional cookies to pass
    headers: additional headers to pass
    json_payload: json to send (POST request only)
    raw_payload: raw payload or multipart payload to send (POST request only)
    touch: whether to use mobile user agent (default true for /touch/* endpoints)
    ignore_cache: whether to not retrieve from/store to cache
    expect_json: whether to expect a json response (useful for webscraping)
    ignore_language: whether to not pass the `lang` parameter
    """

    ignore_cache = method == "post" or ignore_cache == True
    cache_enabled = current_app.config["CACHE_PIXIV_REQUESTS"]

    _cookies = {**cookies}
    _headers = {**headers}
    _params = ""
    cookie_header = ""

    if not ignore_language:
        try:
            lang = request.cookies.get("Vixipy-Language")
        except Exception:
            lang = "en"

        params = params.copy()

        params.append(
            (
                "lang",
                {
                    "en": "en",
                    "ja": "ja",
                    "zh_Hans": "zh",
                    "zh_Hant": "zh_tw",
                    "th": "th",
                    "ms": "ms",
                }.get(lang, "en"),
            )
        )

    for i, v in enumerate(params):
        if v[1] is None:
            continue
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
            "Mozilla/5.0 (Android 10; Mobile; rv:140.0) Gecko/140.0 Firefox/140.0"
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
        if expect_json:
            raise PixivError(await r.text(), r.status, endpoint)
        res = await r.text()
        pass

    if cache_enabled and not ignore_cache:
        await current_app.cache_client.set(
            bytes(f"endpoint_{hashed_value}", "utf-8"),
            bytes(json.dumps(res), "utf-8"),
            int(current_app.config["CACHE_TTL"]),
        )

    done_time = (time.perf_counter() - req_start) * 1000

    log.info("[done] [%dms] [%s]", done_time, endpoint)
    add_server_timing_metric(f"api_{endpoint}", done_time)

    return res
