from flask import current_app

from ..api import getArtworkComments as _getArtworkComments
from ..api import postComment as _postComment
from ..api import postStamp as _postStamp
from ..classes import Comment


def getArtworkComments(_id: int, **kwargs):
    data = [Comment(x) for x in _getArtworkComments(_id, **kwargs)["body"]["comments"]]
    for comment in data:
        for emoji in current_app.config["emojis"]:
            comment.comment = comment.comment.replace(
                f"({emoji})",
                f'<img alt="{emoji}" src="/proxy/s.pximg.net/common/images/emoji/{current_app.config["emojis"][emoji]}.png">',
            )

    return data


def postComment(_id: int, authorId: int, comment: str):
    return _postComment(_id, authorId, comment)


def postStamp(_id: int, authorId: int, stampId: int):
    return _postStamp(_id, authorId, stampId)
