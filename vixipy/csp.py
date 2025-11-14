from __future__ import annotations

from quart import current_app, request
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from quart import Quart, Response


async def csp_handler(r: Response):

    proxy_cookie = request.cookies.get("Vixipy-Image-Proxy")
    proxy_domain = urlparse(proxy_cookie).netloc if proxy_cookie else None

    media_common = "'self' %s blob: data: ; " % (
        proxy_domain
        or (
            current_app.config["IMG_PROXY"]
            if not current_app.config["IMG_PROXY"].startswith("/proxy/i.pximg.net")
            else ""
        ),
    )

    r.headers["Content-Security-Policy"] = (
        "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval' blob: ; "
        "img-src "
        + media_common
        + "media-src "
        + media_common
        + "frame-ancestors 'self'; "
        "style-src 'self' 'unsafe-inline'; "
    )
    return r


def init_app(app: Quart):
    app.after_request(csp_handler)
