from __future__ import annotations

from quart import (
    Blueprint,
    abort,
    current_app,
    request
)

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

bp = Blueprint("proxy", __name__)
log = logging.getLogger("vixipy.routes.proxy")

@bp.get("/proxy/<path:url>")
async def perform_proxy_request(url: str):
    permitted = ("i.pximg.net", "s.pximg.net")

    if url.split("/")[0] not in permitted:
        abort(400)
    
    response_headers = {"Cache-Control": "max-age=31536000"}

    r: ClientResponse = await current_app.content_proxy.get("https://" + url)
    r.raise_for_status()

    response_headers["Content-Type"] = r.headers["Content-Type"]
    if content_length := r.headers.get("content-length"):
        response_headers["Content-Length"] = content_length
    else:
        log.warning("%s has no content length", url)

    async def stream():
        async for chunk in r.content.iter_chunked(10 * 1024):
            yield chunk
    
    return stream(), response_headers

