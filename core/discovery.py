import api

from classes import ArtworkEntry

def getDiscoveryData(mode: str):

    data = api.getDiscovery(mode)["body"]

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]
