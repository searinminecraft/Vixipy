from ..api import (
    getLanding,
    getNovel as _getNovel,
    getRecommendedNovels as _getRecommended,
    getLatestFromFollowing
)
from ..classes import Novel, NovelEntry, NovelSeries


async def getNovel(id: int):
    data = (await _getNovel(id))["body"]
    return Novel(data)


async def getRecommendedNovels(id: int):
    data = await _getRecommended(id)
    return [NovelEntry(x) for x in data["body"]["novels"]]


async def getLatestNovelsFromFollowing(mode: str = "all", p: int = 1):
    data = await getLatestFromFollowing(mode, p, content="novel")
    return [NovelEntry(x) for x in data["body"]["thumbnails"]["illust"]]