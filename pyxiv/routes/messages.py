from __future__ import annotations

from quart import Blueprint, flash, render_template, g, request, redirect, url_for
from ..core import messages
from ..api import pixivReq
from asyncio import gather
from aiohttp import MultipartWriter
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage

bp = Blueprint("messages", __name__)
log = logging.getLogger("vixipy.routes.messages")


@bp.before_request
async def getThreads():
    g.threads = await messages.getMessageThreads()


@bp.get("/self/messages")
async def messagesMain():
    data = await messages.getMessageThreads()
    return await render_template("messages/index.html")


@bp.route("/self/messages/t/<int:thread_id>", methods=("GET", "POST"))
async def messageThread(thread_id: int):
    if request.method == "POST":
        f = await request.form
        files = await request.files
        upfile: FileStorage = files["upfile"]
        text: str = f.get("text")
        fileData = upfile.read()

        if not text and len(fileData) == 0:
            # silently do nothing
            return redirect(
                url_for("messages.messageThread", thread_id=thread_id), code=303
            )

        if len(fileData) > 0:
            log.debug("File detected, using form data payload")
            mp = MultipartWriter("form-data")
            tfd = mp.append(str(thread_id))
            tfd.set_content_disposition("form-data", name="thread_id")
            
            filemp = mp.append(fileData, {"Content-Type": upfile.content_type})
            filemp.set_content_disposition("form-data", name="upfile", filename=upfile.name)

            textmp = mp.append(text)
            textmp.set_content_disposition("form-data", name="text")

            modemp = mp.append("message_thread_content_image_text")
            modemp.set_content_disposition("form-data", name="mode")

            csrfmp = mp.append(g.userPxCSRF)
            csrfmp.set_content_disposition("form-data", name="tt")

            await pixivReq("post", "/rpc/index.php", rawPayload=mp, additionalHeaders={"Referer": "https://www.pixiv.net/messages.php"})
        else:
            log.debug("No file detected. Using regular POST request")
            await messages.sendMessage(thread_id, text)

        return redirect(
            url_for("messages.messageThread", thread_id=thread_id), code=303
        )

    threadData, contents = await gather(
        messages.getMessageThread(thread_id),
        messages.getMessageThreadContents(
            thread_id, max_content_id=request.args.get("max_content_id"), num=50
        ),
    )

    return await render_template(
        "messages/message.html", threadData=threadData, thread=contents
    )
