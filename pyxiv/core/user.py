from .. import api

from ..classes import (
    User,
    UserBookmarks,
    ArtworkEntry,
    UserSettingsState,
    Notification,
    UserFollowData,
)


def getFollowingNew(mode: str, page: int = 1) -> list[ArtworkEntry]:
    """
    Gets new artworks from users you follow
    """

    data = api.getLatestFromFollowing(mode, page)["body"]

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]


def getUser(_id: int) -> User:
    """Get a user"""

    data = api.getUserInfo(_id)["body"]

    return User(data)


def getUserBookmarks(
    _id: int, tag: str = "", offset: int = 0, limit: int = 30
) -> UserBookmarks:
    """Get a user's bookmarks"""
    data = api.getUserBookmarks(_id, tag, offset, limit)["body"]

    return UserBookmarks(data)


def getUserSettingsState():

    return UserSettingsState(api.getUserSettingsState()["body"])


def getNotifications():

    return [Notification(x) for x in api.getNotifications()["body"]["items"]]


def getUserTopIllusts(_id: int):

    data = api.getUserTopIllusts(_id)["body"]
    illusts = [ArtworkEntry(data["illusts"][x]) for x in data["illusts"]]
    manga = [ArtworkEntry(data["manga"][x]) for x in data["manga"]]

    return list(illusts + manga)


def retrieveUserIllusts(_id: int, illustIds: list[int]) -> list[ArtworkEntry]:

    data = api.retrieveUserIllusts(_id, illustIds)["body"]["works"]

    return [ArtworkEntry(data[x]) for x in data]


def getUserFollowing(_id: int, offset: int = 0, limit: int = 30):

    data = api.getUserFollowing(_id, offset, limit)["body"]
    total = data["total"]

    return total, [UserFollowData(x) for x in data["users"]]


def getUserFollowers(_id: int, offset: int = 0, limit: int = 30):

    data = api.getUserFollowers(_id, offset, limit)["body"]
    total = data["total"]

    return total, [UserFollowData(x) for x in data["users"]]
