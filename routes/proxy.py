from flask import Blueprint, render_template
import cfg

import requests

proxy = Blueprint("proxy", __name__, url_prefix="/proxy")

@proxy.route("/<path:proxypath>", methods=["GET"])
def proxyRequest(proxypath):

    # not letting anyone use this for malicious intent :trolley:
    permittedProxies = ("i.pximg.net", "s.pximg.net", "ugoira.com")

    if proxypath.split("/")[0] not in permittedProxies:
        return render_template("error.html", error=f"domain '{proxypath.split('/')[0]}' is not allowed"), 401

    def requestContent():

        headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
        }

        if proxypath.split("/")[0] in ("i.pximg.net", "s.pximg.net"):
            headers["Referer"] = "https://www.pixiv.net"

        with requests.get(f"https://{proxypath}", stream=True,
                          headers=headers) as r:

            for ch in r.iter_content(10*1024):
                yield ch

    return requestContent(), {"Content-Type": None} #  that works somehow
