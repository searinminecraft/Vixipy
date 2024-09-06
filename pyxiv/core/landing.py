from ..api import getLanding, getRanking, getLatestFromFollowing
from ..classes import ArtworkEntry, RecommendByTag, LandingPageLoggedIn, RankingEntry


def getFollowingNew(mode: str, page: int = 1):
    """
    Gets new artworks from users you follow
    """

    data = getLatestFromFollowing(mode, page)["body"]

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]


def getLandingPage(mode: str):
    """
    Gets the landing page.
    """

    data = getLanding(mode)["body"]
    newFromFollowing = getFollowingNew(mode)

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

    return LandingPageLoggedIn(recommended, recommendByTag, newFromFollowing)


def getLandingRanked():

    data = getRanking()["contents"]

    return [RankingEntry(x) for x in data]
