from ..api import getArtworkComments as _getArtworkComments
from ..api import postComment as _postComment
from ..api import postStamp as _postStamp
from ..classes import Comment


def getArtworkComments(_id: int, **kwargs):
    return [Comment(x) for x in _getArtworkComments(_id, **kwargs)["body"]["comments"]]


def postComment(_id: int, authorId: int, comment: str):
    return _postComment(_id, authorId, comment)


def postStamp(_id: int, authorId: int, stampId: int):
    return _postStamp(_id, authorId, stampId)
