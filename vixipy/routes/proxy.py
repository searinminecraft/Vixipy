from __future__ import annotations

from quart import Blueprint, abort, current_app, request, make_response

import logging
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from quart import Response

bp = Blueprint("proxy", __name__)
log = logging.getLogger("vixipy.routes.proxy")


@bp.errorhandler(Exception)
async def handle_exception(e: Exception):
    log.exception("Exception occurred while proxying %s", request.path.removeprefix("/proxy"))
    err = traceback.format_exc()
    return (
        f"""
Unable to proxy because an exception occurred:

{err}
""",
        500,
        {"Content-Type": "text/plain"},
    )


@bp.after_request
async def set_header_common(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


@bp.get("/proxy/ugoira/<int:id>")
async def ugoira_proxy(id: int):
    endpoint = (
        current_app.config.get("UGOIRA_ENDPOINT")
        or "https://t-hk.ugoira.com/ugoira/%s.mp4"
    )
    referer = current_app.config.get("UGOIRA_REFERER") or "https://ugoira.com"

    log.debug("Proxy ugoira %d: Server %s; Referer %s", id, endpoint, referer)

    response_headers = {"Cache-Control": "max-age=31536000"}
    r: ClientResponse = await current_app.content_proxy.get(
        endpoint % id, headers={"Referer": referer}
    )
    r.raise_for_status()

    response_headers["Content-Type"] = r.headers["Content-Type"]
    if content_length := r.headers.get("content-length"):
        response_headers["Content-Length"] = content_length

    async def stream():
        async for chunk in r.content.iter_chunked(10 * 1024):
            yield chunk

    res = await make_response(stream())
    res.timeout = None

    return res, response_headers


@bp.get("/proxy/<path:url>")
async def perform_proxy_request(url: str):
    permitted = ("i.pximg.net", "s.pximg.net")
    url = url.removeprefix("https://")
    url = url.removeprefix("http://")

    if url.split("/")[0] not in permitted:
        return "Nice try :3", 400, {"Content-Type": "text/plain"}

    response_headers = {"Cache-Control": "max-age=31536000"}

    r: ClientResponse = await current_app.content_proxy.get("https://" + url)
    r.raise_for_status()

    response_headers["Content-Type"] = r.headers["Content-Type"]
    if content_length := r.headers.get("content-length"):
        response_headers["Content-Length"] = content_length

    async def stream():
        async for chunk in r.content.iter_chunked(10 * 1024):
            yield chunk
        r.close()

    res = await make_response(stream())
    res.timeout = None

    return res, response_headers


@bp.get("/proxy/3rd_party/profile_image/<platform>/<username>")
async def get_3rdparty_profile_image(platform, username):
    platform_mapping = {
        "github": "https://github.com/%s.png",
        "codeberg": "https://codeberg.org/%s.png"
    }

    if platform not in platform_mapping:
        abort(400)

    response_headers = {"Cache-Control": "max-age=31536000"}

    r: ClientResponse = await current_app.content_proxy.get(platform_mapping[platform] % username)
    r.raise_for_status()

    response_headers["Content-Type"] = r.headers["Content-Type"]
    if content_length := r.headers.get("content-length"):
        response_headers["Content-Length"] = content_length

    async def stream():
        async for chunk in r.content.iter_chunked(10 * 1024):
            yield chunk
        r.close()

    res = await make_response(stream())
    res.timeout = None

    return res, response_headers
