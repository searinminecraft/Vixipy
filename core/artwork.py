import api

from classes import Artwork, ArtworkPage, ArtworkEntry


def getArtwork(_id: int):

    data = api.getArtworkInfo(_id)["body"]
    return Artwork(data)


def getArtworkPages(_id: int):

    data = api.getArtworkPages(_id)["body"]
    return [ArtworkPage(x) for x in data]


def getRelatedArtworks(_id: int, limit: int = 30):

    data = api.getRelatedArtworks(_id, limit)["body"]
    return [ArtworkEntry(x) for x in data["illusts"]]
