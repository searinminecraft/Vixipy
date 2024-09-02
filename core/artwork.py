import api

from classes import Artwork, ArtworkPage

def getArtwork(_id: int):

    data = api.getArtworkInfo(_id)["body"]
    return Artwork(data)

def getArtworkPages(_id: int):

    data = api.getArtworkPages(_id)["body"]
    return [ArtworkPage(x) for x in data]
