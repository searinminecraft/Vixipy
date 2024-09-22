from flask import Blueprint, abort, redirect

from .. import cfg
import requests
import time

proxy = Blueprint("proxy", __name__, url_prefix="/proxy")


@proxy.errorhandler(requests.ConnectionError)
def handleConnectionError(e):
    return f"Unable to complete request due to error: {e}", 500


@proxy.errorhandler(requests.HTTPError)
def handleHttpError(e):
    return f"Unable to complete request due to error: {e}", 500


@proxy.route("/ugoira/<int:_id>")
def retrieveUgoira(_id: int):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Referer": "https://ugoira.com/",
    }
    respHeaders = {"Cache-Control": "max-age=31536000"}

    req = requests.get(
        f"https://t-hk.ugoira.com/ugoira/{_id}.mp4", headers=headers, stream=True
    )
    respHeaders["Content-Type"] = req.headers["Content-Type"]
    respHeaders["Content-Length"] = req.headers["Content-Length"]
    req.raise_for_status()

    def requestContent():

        for ch in req.iter_content(10 * 1024):
            yield ch

        print(f"PROXY    | Completed ugoira request for ID {_id}")

    return requestContent(), respHeaders


# TODO: Caching, so my poor computer won't constantly re-download the porn


@proxy.route("/<path:proxypath>", methods=["GET"])
def proxyRequest(proxypath):

    proxypath = proxypath.replace("https://", "")

    # not letting anyone use this for malicious intent :trolley:
    permittedProxies = ("i.pximg.net", "s.pximg.net")

    if proxypath.split("/")[0] not in permittedProxies:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
    }

    respHeaders = {"Cache-Control": "max-age=31536000"}

    if proxypath.split("/")[0] in ("i.pximg.net", "s.pximg.net"):
        headers["Referer"] = "https://www.pixiv.net"

    # try to get first

    connStart = time.perf_counter()
    r = requests.get(f"https://{proxypath}", stream=True, headers=headers)
    r.raise_for_status()
    connEnd = time.perf_counter()

    respHeaders["Content-Type"] = r.headers["Content-Type"]
    #  sometimes pixiv does not return content-length for whatever reason
    try:
        respHeaders["Content-Length"] = r.headers["Content-Length"]
    except KeyError:
        pass

    def requestContent():

        start = time.perf_counter()

        for ch in r.iter_content(10 * 1024):
            yield ch

        end = time.perf_counter()

        print(
            "PROXY    | Completed proxy request to",
            f"https://{proxypath}",
            f"(Connection start: {round((connEnd - connStart) * 1000)}ms,",
            f"complete stream: {round((end - start) * 1000)}ms)",
        )

        r.close()

    return requestContent(), respHeaders
