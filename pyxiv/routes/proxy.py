from quart import Blueprint, abort, redirect, request, current_app
import aiohttp

from .. import cfg
import time

import logging

log = logging.getLogger("pyxiv.routes.proxy")

proxy = Blueprint("proxy", __name__, url_prefix="/proxy")


@proxy.errorhandler(aiohttp.ClientError)
async def handleHttpError(e):
    return f"Unable to complete request due to error: {e}", 500


@proxy.route("/ugoira/<int:_id>")
async def retrieveUgoira(_id: int):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Referer": "https://ugoira.com/",
    }
    respHeaders = {"Cache-Control": "max-age=31536000"}

    req = await current_app.proxySession.get(
        f"https://t-hk.ugoira.com/ugoira/{_id}.mp4", headers=headers
    )

    respHeaders["Content-Type"] = req.headers["Content-Type"]
    respHeaders["Content-Length"] = req.headers["Content-Length"]
    req.raise_for_status()

    async def requestContent():

        async for ch in req.content.iter_chunked(10 * 1024):
            yield ch

    return requestContent(), respHeaders


# TODO: Caching, so my poor computer won't constantly re-download the porn


@proxy.route("/<path:proxypath>", methods=["GET"])
async def proxyRequest(proxypath):

    proxypath = proxypath.replace("https://", "")

    # not letting anyone use this for malicious intent :trolley:
    permittedProxies = ("i.pximg.net", "s.pximg.net", "embed.pixiv.net")

    if proxypath.split("/")[0] not in permittedProxies:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
    }

    respHeaders = {"Cache-Control": "max-age=31536000"}

    if proxypath.split("/")[0] in ("i.pximg.net", "s.pximg.net"):
        headers["Referer"] = "https://www.pixiv.net"

    if proxypath.split("/")[0] == "embed.pixiv.net":
        proxypath += "?" + request.full_path.split("?")[1]

    cstart = time.perf_counter()
    r = await current_app.proxySession.get("https://" + proxypath, headers=headers)
    r.raise_for_status()
    cend = time.perf_counter()

    respHeaders["content-type"] = r.headers["content-type"]
    if "content-length" in r.headers:
        respHeaders["content-length"] = r.headers["content-length"]

    async def gen():
        sstart = time.perf_counter()
        async for chunk in r.content.iter_chunked(10 * 1024):
            yield chunk
        s_end = time.perf_counter()

        log.debug("Completed proxy request for %s - C: %dms S: %dms", proxypath, (cend - cstart) * 1000, (s_end - sstart) * 1000)

    return gen(), respHeaders
