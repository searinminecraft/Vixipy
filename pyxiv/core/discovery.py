from .. import api

from ..classes import ArtworkEntry


def getDiscoveryData(mode: str, limit: int = 30) -> list[ArtworkEntry]:
    """Get's the discovery data"""

    data = api.getDiscovery(mode, limit)["body"]

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]
