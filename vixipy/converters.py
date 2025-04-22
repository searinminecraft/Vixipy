from quart import current_app
from urllib.parse import urlparse

def proxy(url: str) -> str:
    url = urlparse(url)

    if url.netloc == "i.pximg.net":
        return current_app.config["IMG_PROXY"] + url.path