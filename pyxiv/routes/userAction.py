from flask import Blueprint, g, redirect, render_template, request, flash, url_for

from .. import api
from ..core.user import getUserBookmarks, getNotifications

userAction = Blueprint("userAction", __name__, url_prefix="/self")


@userAction.route("/")
def redirectToSelf():

    return redirect(f"/users/{g.userdata._id}")


@userAction.route("/bookmarks")
def yourBookmarks():

    offset = request.args.get("offset")

    if offset:
        try:
            data = getUserBookmarks(g.userdata._id, offset=offset)
            if len(data.works) > 30:
                r, extra = divmod(data.total, int(offset))
                d, _ = divmod(extra, int(offset))

                canGoPrevious = True
                if d > 0:
                    canGoNext = True
                else:
                    canGoNext = False
            else:
                canGoNext = False
                canGoPrevious = False
        except ZeroDivisionError:
            canGoNext = True
            canGoPrevious = False
    else:
        data = getUserBookmarks(g.userdata._id)
        canGoPrevious = False
        canGoNext = True

    return render_template(
        "bookmarksSelf.html",
        data=data,
        canGoNext=canGoNext,
        canGoPrevious=canGoPrevious,
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
        api.postComment(args["id"], args["author"], form["comment"])
    except Exception as e:
        flash(f"Unable to post comment: {e.__class__.__name__}: {e}", "error")

    return redirect(url_for("artworks.artworkComments", _id=args["id"]))


@userAction.route("/notifications")
def notifications():

    return render_template("notifications.html", data=getNotifications())
