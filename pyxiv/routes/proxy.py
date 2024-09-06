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


# TODO: Caching, so my poor computer won't constantly re-download the porn


@proxy.route("/<path:proxypath>", methods=["GET"])
def proxyRequest(proxypath):

    proxypath = proxypath.replace("https://", "")

    # not letting anyone use this for malicious intent :trolley:
    permittedProxies = ("i.pximg.net", "s.pximg.net", "ugoira.com")

    if proxypath.split("/")[0] not in permittedProxies:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
    }

    respHeaders = {"Cache-Control": "max-age=31536000"}

    if proxypath.split("/")[0] in ("i.pximg.net", "s.pximg.net"):
        headers["Referer"] = "https://www.pixiv.net"

    # try to get first

    r = requests.get(f"https://{proxypath}", stream=True, headers=headers)
    r.raise_for_status()
    respHeaders["Content-Type"] = r.headers["Content-Type"]
    #  sometimes pixiv does not return content-length for whatever reason
    try:
        respHeaders["Content-Length"] = r.headers["Content-Length"]
    except KeyError:
        pass
    r.close()

    def requestContent():

        print(f"Started proxy request to https://{proxypath}")

        start = time.perf_counter()

        with requests.get(f"https://{proxypath}", stream=True, headers=headers) as r:

            for ch in r.iter_content(10 * 1024):
                yield ch

        end = time.perf_counter()

        print(
            f"Completed proxy request https://{proxypath} in {round((end - start) * 1000)}ms"
        )

    return requestContent(), respHeaders
