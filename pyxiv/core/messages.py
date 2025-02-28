from ..api import (
    getMessageThreads as _getMessageThreads,
    getMessageThread as _getMessageThread,
    getMessageThreadContents as _getMessageThreadContents,
    sendMessage as _sendMessage,
)
from ..classes import MessageThread, MessageThreadEntry, MessageThreadContents


async def getMessageThreads() -> list[MessageThread]:
    return [
        MessageThreadEntry(x)
        for x in (await _getMessageThreads(10))["body"]["message_threads"]
    ]


async def getMessageThread(thread_id: int) -> MessageThread:
    return MessageThread(await _getMessageThread(thread_id))


async def getMessageThreadContents(
    thread_id: int, *, max_content_id: int = None, num: int = 10
):
    return MessageThreadContents(
        (await _getMessageThreadContents(thread_id, num, max_content_id))["body"]
    )


async def sendMessage(thread_id: int, message: str) -> None:
    return await _sendMessage(thread_id, message)
