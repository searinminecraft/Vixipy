from ..api import (
    getLanding,
    getNovel as _getNovel,
    getRecommendedNovels as _getRecommended,
    getLatestFromFollowing,
    getNovelSeries as _getNovelSeries,
    getNovelSeriesContents as _getNovelSeriesContents,
    getFrequentTagsNovel
)
from ..classes import Novel, NovelEntry, NovelSeriesEntry, NovelSeries, SimpleTag


async def getNovel(id: int):
    data = (await _getNovel(id))["body"]
    return Novel(data)


async def getRecommendedNovels(id: int):
    data = await _getRecommended(id)
    return [NovelEntry(x) for x in data["body"]["novels"]]


async def getLatestNovelsFromFollowing(mode: str = "all", p: int = 1):
    data = await getLatestFromFollowing(mode, p, content="novel")
    return [NovelEntry(x) for x in data["body"]["thumbnails"]["illust"]]

async def getNovelSeries(id: int):
    data = await _getNovelSeries(id)
    return NovelSeries(data["body"])

async def getNovelSeriesContents(id: int, page: int = 1):
    data = await _getNovelSeriesContents(id, (30*page)-30)
    return [NovelEntry(x) for x in data["body"]["thumbnails"]["novel"]]


async def getFrequentTags(ids: list[int]):
    if len(ids) == 0:
        return []
    return [SimpleTag(x) for x in (await getFrequentTagsNovel(ids))["body"]]
