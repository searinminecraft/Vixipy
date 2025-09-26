from quart import current_app, request, url_for
import re
from urllib.parse import urlparse, quote
from typing import Optional

ARTWORKS_M = re.compile(r"\/artworks\/.+")
NOVEL_M = re.compile(r"\/novel\/show\.php\?id=(\d+).+")
USERS_M = re.compile(r"\/users\/(\d+)")


def proxy(url: str) -> Optional[str]:
    if not url:
        return None

    url = urlparse(url)

    proxy_cookie = request.cookies.get("Vixipy-Image-Proxy")

    if not proxy_cookie:
        proxy = current_app.config["IMG_PROXY"]
    else:
        proxy = proxy_cookie

    if url.netloc == "i.pximg.net":
        return proxy + url.path
    return "/proxy/" + str(
        f"{url.netloc}{url.path}{f'?{url.query}' if url.query else ''}"
    )


def convert_pixiv_link(url: str) -> str:
    if not url:
        return None

    url = urlparse(url)
    path = url.path

    if url.netloc == "www.pixivision.net":
        for l in ("en", "ja", "ko", "zh", "zh-tw"):
            if path.startswith(f"/{l}/"):
                path = path.replace(f"/{l}/", "/")

        if path.startswith("/t/"):
            return url_for("pixivision.tag", id=path.split("/")[2])
        if path.startswith("/a/"):
            return url_for("pixivision.article", id=path.split("/")[2])
        if path.startswith("/c/"):
            return url_for("pixivision.category", c=path.split("/")[2])

    if url.netloc == "www.pixiv.net":
        if path.startswith("/en/"):
            path = path.replace("/en/", "/")

        if path == "" or path == "/":
            return "/"
        if path.startswith("/tags/"):
            return path
        if res := ARTWORKS_M.search(path):
            return res.group(0)
        if res := NOVEL_M.search(path):
            return url_for("novels.novel_main", id=res.group(1))
        if res := USERS_M.search(path):
            return url_for("users.user_profile", user=res.group(1))

    if url.netloc:
        return f"/jump.php?url={quote(url.geturl())}"
    else:
        return url.geturl().replace("/en/", "/")
