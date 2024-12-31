from ..api import searchArtwork as s
from ..api import getTagInfo as gt
from ..classes import SearchResults, TagInfo
from ..utils.filtering import filterEntriesFromPreferences


async def searchArtwork(keyword: str, **kwargs) -> SearchResults:

    data = (await s(keyword, **kwargs))["body"]

    results = SearchResults(data)
    results.popularRecent = filterEntriesFromPreferences(results.popularRecent)
    results.popularAllTime = filterEntriesFromPreferences(results.popularAllTime)
    results.results = filterEntriesFromPreferences(results.results)

    return results


async def getTagInfo(tag: str) -> TagInfo:

    data = (await gt(tag))["body"]

    return TagInfo(data)
