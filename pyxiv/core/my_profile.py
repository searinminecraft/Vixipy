from ..api import getMyProfile
from ..classes import UserMyProfile


async def getProfileConfig():
    return UserMyProfile((await getMyProfile())["body"])
