import api

from classes import ArtworkEntry, RecommendByTag, LandingPageLoggedIn

def getLanding(mode: str):

    data = api.getLanding(mode)["body"]

    artworks = {}
    recommended = []
    recommendByTag = []

    for x in data["thumbnails"]["illust"]:
        artworks[x["id"]] = ArtworkEntry(x)

    for _id in data["page"]["recommend"]["ids"]:
        recommended.append(artworks[_id])

    for idx in data["page"]["recommendByTag"]:
        ids = []
        for _id in idx["ids"]:
            ids.append(artworks[_id])
        recommendByTag.append(RecommendByTag(idx["tag"], ids))

    return LandingPageLoggedIn(recommended, recommendByTag)
