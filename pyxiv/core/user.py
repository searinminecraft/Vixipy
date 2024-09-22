from .. import api

from ..classes import User, UserBookmarks, ArtworkEntry, UserSettingsState


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
