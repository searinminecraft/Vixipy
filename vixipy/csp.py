from __future__ import annotations

from quart import current_app, request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Quart, Response


async def csp_handler(r: Response):
    media_src = "media-src 'self' %s blob: data: ; " % (
        request.cookies.get("Vixipy-Image-Proxy", "")
        or (
            current_app.config["IMG_PROXY"]
            if not current_app.config["IMG_PROXY"].startswith("/proxy/i.pximg.net")
            else ""
        ),
    )

    r.headers["Content-Security-Policy"] = (
        "script-src 'self' 'wasm-unsafe-eval' blob: ; "
        + media_src
        + "frame-ancestors 'self'; "
        "style-src 'self' 'unsafe-inline'; "
    )
    return r


def init_app(app: Quart):
    app.after_request(csp_handler)
