from ..api import getArtworkComments as _getArtworkComments
from ..api import postComment as _postComment
from ..classes import Comment


def getArtworkComments(_id: int, **kwargs):
    return [Comment(x) for x in _getArtworkComments(_id, **kwargs)["body"]["comments"]]


def postComment(_id: int, authorId: int, comment: str):
    return _postComment(_id, authorId, comment)
