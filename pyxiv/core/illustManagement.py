from .. import api
from ..classes import UserInternalIllustDetails


async def getInternalIllustDetails(id: int):
    data = await api.getUserIllustDetails(id)
    return UserInternalIllustDetails(data["body"])
