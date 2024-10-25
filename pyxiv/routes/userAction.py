from flask import Blueprint, g, redirect, render_template, request, flash, url_for

from .. import api
from ..core.comments import postComment, postStamp
from ..core.user import getUserBookmarks, getNotifications

userAction = Blueprint("userAction", __name__, url_prefix="/self")


@userAction.route("/")
def redirectToSelf():

    return redirect(f"/users/{g.userdata._id}")


@userAction.route("/bookmarks")
def yourBookmarks():

    page = int(request.args.get("p", 1))

    data = getUserBookmarks(g.userdata._id, offset=(30 * page) - 30)

    pages, extra = divmod(data.total, 30)

    if extra > 0:
        pages += 1

    return render_template(
        "bookmarksSelf.html",
        data=data,
        pages=pages,
        canGoNext=(page < pages and not page == pages),
        canGoPrevious=(not page == 1),
    )


@userAction.route("/addbookmark/<int:_id>")
def addBookmark(_id: int):

    api.pixivPostReq(
        "/ajax/illusts/bookmarks/add",
        jsonPayload={"illust_id": str(_id), "restrict": 0, "comment": "", "tags": []},
    )

    return redirect(request.args["r"])


@userAction.route("/removebookmark/<int:_id>")
def deleteBookmark(_id: int):

    api.pixivPostReq("/ajax/illusts/bookmarks/delete", rawPayload=f"bookmark_id={_id}")

    return redirect(request.args["r"])


@userAction.route("/like/<int:_id>")
def likeIllust(_id: int):

    api.pixivPostReq("/ajax/illusts/like", jsonPayload={"illust_id": str(_id)})

    return redirect(request.args["r"])


@userAction.post("/comment")
def comment():
    args = request.args
    form = request.form
    try:
        postComment(args["id"], args["author"], form["comment"])
    except Exception as e:
        flash(f"Unable to post comment: {e.__class__.__name__}: {e}", "error")

    return redirect(url_for("artworks.artworkComments", _id=args["id"]))


@userAction.post("/postStamp")
def stamp():
    args = request.args
    form = request.form
    try:
        postStamp(args["id"], args["author"], form["stampId"])
    except Exception as e:
        flash(f"Unable to send stamp: {e.__class__.__name__}: {e}", "error")

    return redirect(url_for("artworks.artworkComments", _id=args["id"]))


@userAction.route("/notifications")
def notifications():

    return render_template("notifications.html", data=getNotifications())
