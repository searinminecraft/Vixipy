from .. import api

from ..classes import Artwork, ArtworkPage, ArtworkEntry, Ranking, SimpleTag
from ..utils.filtering import filterEntriesFromPreferences


async def getArtwork(_id: int) -> Artwork:
    """Get information about an artwork"""

    data = (await api.getArtworkInfo(_id))["body"]
    return Artwork(data)


async def getArtworkPages(_id: int) -> list[ArtworkPage]:
    """Get the pages of the artwork"""

    data = (await api.getArtworkPages(_id))["body"]
    return [ArtworkPage(x) for x in data]


async def getRelatedArtworks(_id: int, limit: int = 30) -> list[ArtworkEntry]:
    """Get's the related artworks for the specified artwork ID"""

    data = (await api.getRelatedArtworks(_id, limit))["body"]
    return filterEntriesFromPreferences([ArtworkEntry(x) for x in data["illusts"]])


async def getRanking(
    mode: str = "daily", date: int = None, content: str = None, p: int = 1
):
    """Get ranking"""

    data = await api.getRanking(mode=mode, date=date, content=content, p=p)
    return Ranking(data)


async def getFrequentTags(ids: list[int]):
    return [SimpleTag(x) for x in (await api.getFrequentTags(ids))["body"]]
