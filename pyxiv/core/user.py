from .. import api

from ..classes import (
    User,
    UserBookmarks,
    ArtworkEntry,
    UserSettingsState,
    Notification,
    UserFollowData,
    PartialUser,
)
from ..utils.filtering import filterEntriesFromPreferences


async def getFollowingNew(mode: str, page: int = 1) -> list[ArtworkEntry]:
    """
    Gets new artworks from users you follow
    """

    data = (await api.getLatestFromFollowing(mode, page))["body"]

    return filterEntriesFromPreferences(
        [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]
    )


async def getUser(_id: int, full: bool = True) -> User:
    """Get a user"""

    try:
        int(_id)
    except Exception:
        raise ValueError from None

    data = (await api.getUserInfo(_id, full))["body"]

    return User(data) if full else PartialUser(data)


async def getUserBookmarks(
    _id: int, tag: str = "", offset: int = 0, limit: int = 30
) -> UserBookmarks:
    """Get a user's bookmarks"""
    data = (await api.getUserBookmarks(_id, tag, offset, limit))["body"]

    bookmarks = UserBookmarks(data)
    bookmarks.works = filterEntriesFromPreferences(bookmarks.works)
    return bookmarks


async def getUserSettingsState():

    return UserSettingsState((await api.getUserSettingsState())["body"])


async def getNotifications():

    return [Notification(x) for x in (await api.getNotifications())["body"]["items"]]


async def getUserTopIllusts(_id: int):

    data = (await api.getUserTopIllusts(_id))["body"]
    illusts = [ArtworkEntry(data["illusts"][x]) for x in data["illusts"]]
    manga = [ArtworkEntry(data["manga"][x]) for x in data["manga"]]

    return filterEntriesFromPreferences(list(illusts + manga))


async def retrieveUserIllusts(_id: int, illustIds: list[int]) -> list[ArtworkEntry]:

    data = (await api.retrieveUserIllusts(_id, illustIds))["body"]["works"]

    return filterEntriesFromPreferences([ArtworkEntry(data[x]) for x in data])


async def getUserFollowing(_id: int, offset: int = 0, limit: int = 30):

    data = (await api.getUserFollowing(_id, offset, limit))["body"]
    total = data["total"]

    return total, [UserFollowData(x) for x in data["users"]]


async def getUserFollowers(_id: int, offset: int = 0, limit: int = 30):

    data = (await api.getUserFollowers(_id, offset, limit))["body"]
    total = data["total"]

    return total, [UserFollowData(x) for x in data["users"]]
