from quart import Blueprint, flash, render_template, g, request, redirect, url_for
from ..core import messages
from asyncio import gather

bp = Blueprint("messages", __name__)


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
        text = f["text"]
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
