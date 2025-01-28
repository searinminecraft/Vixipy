from .. import api
from ..classes import NewsArticle

async def getNewsEntry(id: int):
    data = await api.getNewsEntry(id)
    return NewsArticle(data["body"])
