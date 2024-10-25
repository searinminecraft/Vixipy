from ..api import getLanding, getRanking, getRecommendedUsers
from ..classes import (
    ArtworkEntry,
    RecommendByTag,
    LandingPageLoggedIn,
    RankingEntry,
    RecommendedUser,
)
from ..core.user import getFollowingNew
from ..utils.filtering import filterEntriesFromPreferences


def _getRecommendedUsers(limit: int = 10):
    """Get recommended users"""

    data = getRecommendedUsers(limit)["body"]

    res = []
    artworks = {}
    users = {}

    for a in data["thumbnails"]["illust"]:
        artworks[int(a["id"])] = a

    for u in data["users"]:
        users[int(u["userId"])] = u

    for r in data["recommendedUsers"]:
        recent = []
        for ar in r["recentIllustIds"]:
            recent.append(ArtworkEntry(artworks[int(ar)]))

        res.append(RecommendedUser(users[int(r["userId"])], recent))

    return res


def getLandingPage(mode: str) -> LandingPageLoggedIn:
    """
    Gets the landing page.
    """

    data = getLanding(mode)["body"]
    newFromFollowing = getFollowingNew(mode)
    recommendedUsers = _getRecommendedUsers()

    artworks = {}
    recommended = []
    recommendByTag = []

    for x in data["thumbnails"]["illust"]:
        artworks[x["id"]] = ArtworkEntry(x)

    for _id in data["page"]["recommend"]["ids"]:
        if _id in artworks:
            recommended.append(artworks[_id])
        else:
            print("Not appending ", _id, "- not returned by pixiv")

    for idx in data["page"]["recommendByTag"]:
        ids = []
        for _id in idx["ids"]:
            if _id in artworks:
                ids.append(artworks[_id])

        res = RecommendByTag(idx["tag"], ids)
        res.artworks = filterEntriesFromPreferences(res.artworks)
        recommendByTag.append(res)

    return LandingPageLoggedIn(
        filterEntriesFromPreferences(recommended),
        recommendByTag,
        newFromFollowing,
        recommendedUsers,
    )


def getLandingRanked() -> list[RankingEntry]:

    data = getRanking()["contents"]

    return [RankingEntry(x) for x in data]
