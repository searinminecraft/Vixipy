from .. import api

from ..classes import Artwork, ArtworkPage, ArtworkEntry


def getArtwork(_id: int):
    """Get information about an artwork"""

    data = api.getArtworkInfo(_id)["body"]
    return Artwork(data)


def getArtworkPages(_id: int):
    """Get the pages of the artwork"""

    data = api.getArtworkPages(_id)["body"]
    return [ArtworkPage(x) for x in data]


def getRelatedArtworks(_id: int, limit: int = 30):
    """Get's the related artworks for the specified artwork ID"""

    data = api.getRelatedArtworks(_id, limit)["body"]
    return [ArtworkEntry(x) for x in data["illusts"]]
