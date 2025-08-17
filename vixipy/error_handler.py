from __future__ import annotations
from typing import TYPE_CHECKING

from .api import PixivError
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
    return await render_template("no_connection.html", exc=str(e))


async def handle_ratelimit_error(e):
    if request.headers.get("hx-request") == "true":
        code = 200
    else:
        code = 429
    return await render_template("ratelimited.html"), code


async def handle_internal_error(e):
    if isinstance(e, HTTPException):
        return e
    log.exception("Exception occurred here:")
    return await render_template("internal_server_error.html", traceback=traceback.format_exc())


def init_app(app: Quart):
    app.register_error_handler(ClientError, on_client_error)
    app.register_error_handler(429, handle_ratelimit_error)
    app.register_error_handler(Exception, handle_internal_error)
