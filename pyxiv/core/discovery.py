from .. import api

from ..classes import ArtworkEntry


def getDiscoveryData(mode: str, limit: int = 30) -> list[ArtworkEntry]:
    """Gets the discovery data"""

    data = api.getDiscovery(mode, limit)["body"]

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]


def getNewestArtworks() -> list[ArtworkEntry]:
    """Get newest artworks"""

    data = api.getNewestArtworks()["body"]

    return [ArtworkEntry(x) for x in data["illusts"]]
