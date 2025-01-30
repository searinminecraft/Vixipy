from quart import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    flash,
    url_for,
    abort,
)
from quart_babel import _

from .. import api
from ..core.comments import postComment, postStamp
from ..core.user import getUserBookmarks, getNotifications
from ..core.artwork import getFrequentTags
from ..core.comments import getReplyAndRoot

import logging

log = logging.getLogger("pyxiv.routes.userAction")


userAction = Blueprint("userAction", __name__, url_prefix="/self")


@userAction.route("/")
async def redirectToSelf():

    return await redirect(f"/users/{g.userdata._id}")


@userAction.route("/bookmarks")
async def yourBookmarks():

    page = int(request.args.get("p", 1))

    data = await getUserBookmarks(g.userdata._id, offset=(48 * page) - 48, limit=48)
    frequent = await getFrequentTags([x._id for x in data.works])

    pages, extra = divmod(data.total, 48)

    if extra > 0:
        pages += 1

    return await render_template(
        "bookmarksSelf.html",
        data=data,
        pages=pages,
        frequent=frequent,
        canGoNext=(page < pages and not page == pages),
        canGoPrevious=(not page == 1),
    )


@userAction.route("/addbookmark/<int:_id>")
async def addBookmark(_id: int):

    await api.pixivReq(
        "post",
        "/ajax/illusts/bookmarks/add",
        jsonPayload={"illust_id": str(_id), "restrict": 0, "comment": "", "tags": []},
    )

    await flash(_("Successfully bookmarked post"))
    return redirect(request.args["r"])


@userAction.route("/removebookmark/<int:_id>")
async def deleteBookmark(_id: int):

    await api.pixivReq(
        "post", "/ajax/illusts/bookmarks/delete", rawPayload=f"bookmark_id={_id}"
    )

    await flash(_("Successfully removed bookmark"))
    return redirect(request.args["r"])


@userAction.route("/like/<int:_id>")
async def likeIllust(_id: int):

    await api.pixivReq(
        "post", "/ajax/illusts/like", jsonPayload={"illust_id": str(_id)}
    )

    await flash(_("Successfully liked post"))
    return redirect(request.args["r"])


@userAction.post("/comment")
async def comment():
    args = request.args
    form = await request.form
    try:
        await postComment(args["id"], args["author"], form["comment"])
    except Exception as e:
        log.exception("Unable to post comment")
        await flash(
            _(
                "Unable to post comment: %(errorClass)s: %(error)s",
                errorClass=e.__class__.__name__,
                error=str(e),
            ),
            "error",
        )
    else:
        await flash(_("Successfully posted comment"))

    return redirect(url_for("artworks.artworkComments", _id=args["id"]))


@userAction.post("/postStamp")
async def stamp():
    args = request.args
    form = await request.form
    try:
        await postStamp(args["id"], args["author"], form["stampId"])
    except Exception as e:
        log.exception("Unable to post stamp")
        await flash(
            _(
                "Unable to send stamp: %(errorClass)s: %(error)s",
                errorClass=e.__class__.__name__,
                error=str(e),
            ),
            "error",
        )
    else:
        await flash(_("Successfully sent stamp"))

    return redirect(url_for("artworks.artworkComments", _id=args["id"]))


@userAction.route("/notifications")
async def notifications():

    return await render_template("notifications.html", data=await getNotifications())


@userAction.post("/favorite_tags/save")
async def addTagToFavorites():
    await api.addTagToFavorites(request.form["tag"])
    return await redirect(request.args.get("r", "/"))


@userAction.route("/followUser/<int:_id>")
async def followUser(_id: int):
    restrict = bool(int(request.args.get("restrict", 0)))
    r = request.args.get("r", "/")

    if _id == 0:
        await flash(_("Invalid user"), "error")
        return await redirect(r, code=303)
    try:
        await api.followUser(_id, restrict)
    except api.PixivError:
        await flash(_("Could not follow user"), "error")
    else:
        await flash(_("Successfully followed user"))
    return redirect(r, code=303)


@userAction.route("/unfollowUser/<int:_id>")
async def unfollowUser(_id: int):
    r = request.args.get("r", "/")
    if _id == 0:
        await flash(_("Invalid user"), "error")
        return await redirect(r, code=303)
    try:
        await api.unfollowUser(_id)
    except api.PixivError:
        await flash(_("Could not unfollow user"), "error")
    else:
        await flash(_("Successfully unfollowed user"))
    return redirect(r, code=303)


@userAction.route("/reply_and_root")
async def replyAndRoot():
    if not request.args.get("illust_id") or not request.args.get("comment_id"):
        abort(400)

    child, root = await getReplyAndRoot(
        request.args.get("illust_id"), request.args.get("comment_id")
    )
    return await render_template("reply_and_root.html", child=child, root=root)
