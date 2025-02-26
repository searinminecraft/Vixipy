from quart import current_app

from ..api import getArtworkComments as _getArtworkComments
from ..api import getArtworkReplies as _getArtworkReplies
from ..api import postComment as _postComment
from ..api import postStamp as _postStamp
from ..api import deleteComment as _deleteComment
from ..api import getReplyAndRoot as _getReplyAndRoot
from ..classes import Comment, CommentReply


async def getArtworkComments(_id: int, **kwargs):
    data: list[Comment] = [
        Comment(x)
        for x in (await _getArtworkComments(_id, **kwargs))["body"]["comments"]
    ]
    for comment in data:
        for emoji in current_app.config["emojis"]:
            comment.comment = comment.comment.replace(
                f"({emoji})",
                f'<img alt="{emoji}" src="/proxy/s.pximg.net/common/images/emoji/{current_app.config["emojis"][emoji]}.png">',
            )

    return data


async def getArtworkReplies(commentId: int):
    res = (await _getArtworkReplies(commentId))["body"]

    data = [CommentReply(x) for x in res["comments"]]
    for comment in data:
        for emoji in current_app.config["emojis"]:
            comment.comment = comment.comment.replace(
                f"({emoji})",
                f'<img alt="{emoji}" src="/proxy/s.pximg.net/common/images/emoji/{current_app.config["emojis"][emoji]}.png">',
            )

    return data


async def postComment(_id: int, authorId: int, comment: str):
    return await _postComment(_id, authorId, comment)


async def deleteComment(_id: int, comment_id: int):
    return await _deleteComment(_id, comment_id)


async def postStamp(_id: int, authorId: int, stampId: int):
    return await _postStamp(_id, authorId, stampId)


async def getReplyAndRoot(illust_id: int, comment_id: int):
    data = (await _getReplyAndRoot(illust_id, comment_id))["body"]
    child = [CommentReply(x) for x in data["child"]["comments"]]
    root = CommentReply(data["root"]["comments"][0])
    return child, root
