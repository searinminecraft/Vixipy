from .. import api

from ..classes import User


def getUser(_id: int):

    data = api.getUserInfo(_id)["body"]

    return User(data)
