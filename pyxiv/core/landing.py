from ..api import getLanding, getRanking
from ..classes import ArtworkEntry, RecommendByTag, LandingPageLoggedIn, RankingEntry
from ..core.user import getFollowingNew
from ..utils.filtering import filterEntriesFromPreferences

def getLandingPage(mode: str) -> LandingPageLoggedIn:
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
            if _id in artworks:
                ids.append(artworks[_id])

        recommendByTag.append(RecommendByTag(idx["tag"], ids))

    return LandingPageLoggedIn(filterEntriesFromPreferences(recommended), recommendByTag, newFromFollowing)


def getLandingRanked() -> list[RankingEntry]:

    data = getRanking()["contents"]

    return [RankingEntry(x) for x in data]
