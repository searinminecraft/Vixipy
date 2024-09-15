from .. import api

from ..classes import ArtworkEntry
from ..utils.filtering import filterEntriesFromPreferences


def getDiscoveryData(mode: str, limit: int = 30) -> list[ArtworkEntry]:
    """Gets the discovery data"""

    data = api.getDiscovery(mode, limit)["body"]

    return filterEntriesFromPreferences(
        [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]
    )


def getNewestArtworks() -> list[ArtworkEntry]:
    """Get newest artworks"""

    data = api.getNewestArtworks()["body"]

    return filterEntriesFromPreferences([ArtworkEntry(x) for x in data["illusts"]])
