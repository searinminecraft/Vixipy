from __future__ import annotations
from typing import TYPE_CHECKING

from .api.handler import PixivError
from .routes.api import handle_bad_request as api_handle_bad_request
from quart import render_template, make_response, request
from werkzeug.exceptions import HTTPException
from http import HTTPStatus
from aiohttp.client_exceptions import ClientError
import logging
import traceback

if TYPE_CHECKING:
    from quart import Quart

log = logging.getLogger("vixipy")


async def on_client_error(e: ClientError):
    log.exception("Network error")
    return await render_template("no_connection.html.j2", exc=str(e))


async def handle_ratelimit_error(e):
    log.warn(
        "[%s] [%s] rate limited on endpoint %s",
        request.headers.get("X-Forwarded-For") or request.remote_addr,
        request.user_agent,
        request.path,
    )
    if request.headers.get("hx-request") == "true":
        code = 200
    else:
        code = 429
    return await render_template("ratelimited.html.j2"), code


async def handle_internal_error(e):
    hx = request.headers.get("hx-request") == "true"

    if isinstance(e, HTTPException):
        if request.path.startswith("/api"):
            if e.code == 404:
                return {
                    "error": True,
                    "message": "The requested endpoint could not be found",
                    "body": [],
                }, 404
            return await api_handle_bad_request(e)

        return await render_template("http_error.html.j2", error=e), 200 if hx else e.code

    log.exception("Exception occurred here:")
    return await render_template(
        "internal_server_error.html.j2", traceback=traceback.format_exc()
    ), (200 if hx else 500)


def init_app(app: Quart):
    app.register_error_handler(ClientError, on_client_error)
    app.register_error_handler(429, handle_ratelimit_error)
    app.register_error_handler(Exception, handle_internal_error)
