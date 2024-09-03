from .. import api

from ..classes import User


def getUser(_id: int):
    """Get a user"""

    data = api.getUserInfo(_id)["body"]

    return User(data)
