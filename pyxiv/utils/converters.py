from quart import g
from urllib.parse import quote, urlparse


def makeJumpPhp(url: str) -> str:
    # NOTE: doesn't seem like this checks if url is from pixiv, so this may catch other urls (https://example.com/artworks/1234 for example), might be good to fix?

    _url = urlparse(url)

    if _url.netloc == "www.pixiv.net":
        if _url.path == "" or _url.path == "/":
            return "/"
        if _url.path.startswith("/info.php"):
            return f"/news/{_url.query.split('=')[1]}"
        if _url.path.startswith("/artworks"):
            return f"/artworks/{_url.path.split('/').pop()}"
        if _url.path.startswith("/users"):
            return _url.path

    return f"/jump.php?url={quote(url)}"


def makeProxy(url: str) -> str:

    if not url:
        return None

    if (g.userProxyServer or g.userProxyServer != "") and (
        url.split("/")[2] in "i.pximg.net"
    ):

        # some users might use a private one, usually just an IP
        # and port, and might contain not just the domain,

        protocol = g.userProxyServer.split("/")[0].replace(":", "")
        if protocol not in ("http", "https"):

            # assume its https
            protocol = "https"

        server = g.userProxyServer.replace(f"{protocol}://", "")
        return url.replace("https://i.pximg.net", f"{protocol}://{server}")

    return url.replace("https://", "/proxy/")
