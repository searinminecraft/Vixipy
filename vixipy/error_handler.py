from __future__ import annotations
from typing import TYPE_CHECKING

from .api import PixivError
from quart import render_template

if TYPE_CHECKING:
    from quart import Quart

async def on_pixiv_error(e: PixivError):
    return await render_template("error.html", message=e)

def init_app(app: Quart):
    app.register_error_handler(PixivError, on_pixiv_error)
