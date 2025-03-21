from ..api import (
    getLanding,
    getNovel as _getNovel,
    getRecommendedNovels as _getRecommended
)
from ..classes import Novel, NovelEntry, NovelSeries


async def getNovel(id: int):
    data = (await _getNovel(id))["body"]
    return Novel(data)


async def getRecommendedNovels(id: int):
    data = await _getRecommended(id)
    return [NovelEntry(x) for x in data["body"]["novels"]]