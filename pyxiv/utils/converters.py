from flask import g


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
