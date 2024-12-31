from .. import api

from ..classes import ArtworkEntry
from ..utils.filtering import filterEntriesFromPreferences


async def getDiscoveryData(mode: str, limit: int = 30) -> list[ArtworkEntry]:
    """Gets the discovery data"""

    data = (await api.getDiscovery(mode, limit))["body"]

    return filterEntriesFromPreferences(
        [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]
    )


async def getNewestArtworks(
    lastId: int = 0, limit: int = 20, _type: str = "illust", r18: bool = False
) -> list[ArtworkEntry]:
    """Get newest artworks"""

    data = (await api.getNewestArtworks(lastId, limit, _type, r18))["body"]

    return filterEntriesFromPreferences([ArtworkEntry(x) for x in data["illusts"]])
