from quart import current_app, request, url_for
import re
from urllib.parse import urlparse, quote

ARTWORKS_M = re.compile(r"\/artworks\/.+")
NOVEL_M = re.compile(r"\/novel\/show\.php\?id=(\d+).+")

def proxy(url: str) -> str:
    url = urlparse(url)

    proxy_cookie = request.cookies.get("Vixipy-Image-Proxy")

    if not proxy_cookie:
        proxy = current_app.config["IMG_PROXY"]
    else:
        proxy = proxy_cookie

    if url.netloc == "i.pximg.net":
        return proxy + url.path
    return "/proxy/" + str(url.netloc + url.path)

def convert_pixiv_link(url: str) -> str:
    url = urlparse(url)
    path = url.path

    if path.startswith("/en/"):
        path = path.replace("/en/", "/")

    if url.netloc == "www.pixiv.net":
        if path == "" or path == "/":
            return "/"
        if res := ARTWORKS_M.search(path):
            return res.group(0)
        if res := NOVEL_M.search(path):
            return url_for("novels.novel_main", id=res.group(1))

        return f"/jump.php?url={quote(url.geturl())}" #  unhandled pixiv link (e.g. /contest/)
    else:
        if url.netloc:
            return f"/jump.php?url={quote(url.geturl())}"
        else:
            return url.geturl().replace("/en/", "/")
