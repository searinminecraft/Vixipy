from quart import current_app, request
from urllib.parse import urlparse


def proxy(url: str) -> str:
    url = urlparse(url)

    proxy_cookie = request.cookies.get("Vixipy-Image-Proxy")

    if not proxy_cookie:
        proxy = current_app.config["IMG_PROXY"]
    else:
        proxy = proxy_cookie

    if url.netloc == "i.pximg.net":
        return proxy + "/" + url.path
    return "/proxy/" + str(url.netloc + url.path)
