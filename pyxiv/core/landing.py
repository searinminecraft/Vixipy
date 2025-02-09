from ..api import getLanding, getRanking, getRecommendedUsers
from ..classes import (
    ArtworkEntry,
    RecommendByTag,
    LandingPageLoggedIn,
    LandingPageManga,
    RankingEntry,
    RecommendedUser,
    PixivisionEntry,
    SimpleTag,
    TrendingTag,
)
from asyncio import gather
import random
from ..core.user import getFollowingNew
from ..utils.filtering import filterEntriesFromPreferences

import logging

log = logging.getLogger("pyxiv.core.landing")


async def _getRecommendedUsers(limit: int = 10):
    """Get recommended users"""

    data = (await getRecommendedUsers(limit))["body"]

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


async def getLandingPage(mode: str) -> LandingPageLoggedIn:
    """
    Gets the landing page.
    """

    data, newFromFollowing, recommendedUsers = await gather(
        getLanding(mode),
        getFollowingNew(mode),
        _getRecommendedUsers(),
    )
    data = data["body"]

    artworks = {}
    recommended = []
    recommendByTag = []
    tags = []
    trendingTags = []

    for x in data["thumbnails"]["illust"]:
        artworks[x["id"]] = ArtworkEntry(x)

    for _id in data["page"]["recommend"]["ids"]:
        if _id in artworks:
            recommended.append(artworks[_id])
        else:
            log.debug("Not appending " + _id + "- not returned by pixiv")

    for idx in data["page"]["recommendByTag"]:
        ids = []
        for _id in idx["ids"]:
            if _id in artworks:
                ids.append(artworks[_id])

        res = RecommendByTag(idx["tag"], ids)
        res.artworks = filterEntriesFromPreferences(res.artworks)
        recommendByTag.append(res)

    for tag in data["page"]["tags"]:
        if tag["tag"] in data["tagTranslation"]:
            translation = data["tagTranslation"][tag["tag"]].get("en")
        else:
            translation = None
        tags.append(SimpleTag({"tag": tag["tag"], "tag_translation": translation}))

    for tt in data["page"]["trendingTags"]:
        try:
            name = tt["tag"]
            ttData = artworks[str(random.choice(tt["ids"]))]
            rate = tt["trendingRate"]
            try:
                translation = data["tagTranslation"][tt["tag"]].get("en")
            except KeyError:
                translation = None
            log.debug(
                "Trending tag: %s, data: %s, img: %s, translation: %s, rate: %d",
                name,
                ttData,
                ttData.thumbUrl,
                translation,
                tt["trendingRate"],
            )
            trendingTags.append(TrendingTag(name, ttData, translation, rate))
        except Exception:
            log.exception("Error trying to parse trending tags")

    pvArticles = [PixivisionEntry(x) for x in data["page"]["pixivision"]]
    trendingTags.sort(key=lambda k: k.trendingRate, reverse=True)
    log.debug(trendingTags)

    return LandingPageLoggedIn(
        filterEntriesFromPreferences(recommended),
        recommendByTag,
        newFromFollowing,
        recommendedUsers,
        pvArticles,
        tags,
        trendingTags,
    )


async def getLandingManga(mode):
    data = (await getLanding(mode, "manga"))["body"]

    artworks = {}
    recommended = []
    tags = []

    for x in data["thumbnails"]["illust"]:
        artworks[x["id"]] = ArtworkEntry(x)

    for _id in data["page"]["recommend"]["ids"]:
        if _id in artworks:
            recommended.append(artworks[_id])
        else:
            log.debug("Not appending ", _id, "- not returned by pixiv")

    for tag in data["page"]["tags"]:
        if tag["tag"] in data["tagTranslation"]:
            translation = data["tagTranslation"][tag["tag"]].get("en")
        else:
            translation = None
        tags.append(SimpleTag({"tag": tag["tag"], "tag_translation": translation}))

    return LandingPageManga(
        filterEntriesFromPreferences(recommended),
        tags,
    )


async def getLandingRanked() -> list[RankingEntry]:

    data = (await getRanking())["contents"]

    return [RankingEntry(x) for x in data]
