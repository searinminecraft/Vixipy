from .. import api

from ..classes import ArtworkEntry


def getDiscoveryData(mode: str, limit: int = 30):

    data = api.getDiscovery(mode, limit)["body"]

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]
