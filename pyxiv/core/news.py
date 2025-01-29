from .. import api
from ..classes import NewsEntry, NewsArticle


async def getNewsEntry(id: int):
    data = await api.getNewsEntry(id)
    return NewsArticle(data["body"])


async def getNews():
    data = await api.getNews()
    res = {}
    for c in data["body"]["categoryTopEntries"]:
        entries = []
        for article in data["body"]["categoryTopEntries"][c]:
            entries.append(NewsEntry(article))
        res[c] = entries

    return res

async def getNewsByCategory(cid: int):
    data = await api.getNewsEntries(cid)
    return [NewsEntry(x) for x in data["body"]["entries"]]
