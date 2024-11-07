from .. import api

from ..classes import Artwork, ArtworkPage, ArtworkEntry, Ranking
from ..utils.filtering import filterEntriesFromPreferences


def getArtwork(_id: int) -> Artwork:
    """Get information about an artwork"""

    data = api.getArtworkInfo(_id)["body"]
    return Artwork(data)


def getArtworkPages(_id: int) -> list[ArtworkPage]:
    """Get the pages of the artwork"""

    data = api.getArtworkPages(_id)["body"]
    return [ArtworkPage(x) for x in data]


def getRelatedArtworks(_id: int, limit: int = 30) -> list[ArtworkEntry]:
    """Get's the related artworks for the specified artwork ID"""

    data = api.getRelatedArtworks(_id, limit)["body"]
    return filterEntriesFromPreferences([ArtworkEntry(x) for x in data["illusts"]])

def getRanking(mode: str = "daily", date: int = None, content: str = None, p: int = 1):
    """Get ranking"""

    data = api.getRanking(mode=mode, date=date, content=content, p=p)
    return Ranking(data)
