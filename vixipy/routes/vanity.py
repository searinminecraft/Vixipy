from quart import Blueprint, redirect
from aiohttp import ClientSession
from urllib.parse import urlparse
import logging

bp = Blueprint("vanity", __name__)

log = logging.getLogger("vixipy.routes.vanity")


@bp.get("/@<name>")
async def pixivme_handle(name):
    async with ClientSession("https://pixiv.me") as s:
        async with s.get(name, allow_redirects=False) as r:
            r.raise_for_status()
            loc = urlparse(r.headers["Location"]).path
            log.info("pixiv.me: Probably found %s -> %s", name, loc)
            return redirect(loc)
