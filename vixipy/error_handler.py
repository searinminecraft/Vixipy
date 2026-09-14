from __future__ import annotations
from typing import TYPE_CHECKING

from .api.handler import PixivError
from .routes.api import handle_bad_request as api_handle_bad_request
from quart import current_app, render_template, make_response, request
from werkzeug.exceptions import HTTPException
from http import HTTPStatus
from aiohttp.client_exceptions import ClientError
import logging
import traceback
import sys

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

        return await render_template("http_error.html.j2", error=e), e.code

    log.exception("Exception occurred here:")

    tb_str = ""
    tb_str += f"{e.__class__.__name__}: {e}\n\n"

    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        for x in traceback.extract_tb(e.__traceback__)[::-1]:
            tb_str += f"at {'/'.join(x.filename.split('/')[-2:])}:{x.lineno}:{x.colno} in {x.name + '()' if '<' not in x.name else x.name}\n"
        tb_str += "\n(Run Vixipy in debug mode to see full traceback)"
    else:
        tb_str += "Instance is using Python 3.11 or below. Contact the system administrator to get a traceback."

    return (
        await render_template(
            "internal_server_error.html.j2", traceback=tb_str if not current_app.config["DEBUG"] else traceback.format_exc()
        ),
        500,
    )


def init_app(app: Quart):
    app.register_error_handler(ClientError, on_client_error)
    app.register_error_handler(429, handle_ratelimit_error)
    app.register_error_handler(Exception, handle_internal_error)
