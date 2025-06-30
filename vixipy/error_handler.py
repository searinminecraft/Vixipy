from __future__ import annotations
from typing import TYPE_CHECKING

from .api import PixivError
from quart import render_template, make_response, request
from werkzeug.exceptions import HTTPException
from http import HTTPStatus
from aiohttp.client_exceptions import ClientError
import logging

if TYPE_CHECKING:
    from quart import Quart

log = logging.getLogger("vixipy")


async def on_pixiv_error(e: PixivError):

    if request.headers.get("X-Vixipy-Quick-Action") == "true":
        return "", 500, {"X-Pixiv-Status-Code": f"{e.code} {HTTPStatus(e.code).name}"}

    res = await make_response(await render_template("error.html", message=str(e)))

    res.headers["X-Pixiv-Status-Code"] = f"{e.code} {HTTPStatus(e.code).name}"

    return res, 500


async def on_client_error(e: ClientError):
    return await render_template("no_connection.html", exc=str(e))


async def handle_ratelimit_error(e):
    return await render_template("ratelimited.html")


async def handle_internal_error(e):
    if isinstance(e, HTTPException):
        raise
    log.exception("Exception occurred here:")
    return await render_template("internal_server_error.html")


def init_app(app: Quart):
    app.register_error_handler(PixivError, on_pixiv_error)
    app.register_error_handler(ClientError, on_client_error)
    app.register_error_handler(429, handle_ratelimit_error)


#    app.register_error_handler(Exception, handle_internal_error)
