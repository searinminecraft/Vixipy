from ..api import searchArtwork as s
from ..api import getTagInfo as gt
from ..classes import SearchResults, TagInfo


def searchArtwork(keyword: str, **kwargs) -> SearchResults:

    data = s(keyword, **kwargs)["body"]

    return SearchResults(data)


def getTagInfo(tag: str) -> TagInfo:

    data = gt(tag)["body"]

    return TagInfo(data)
