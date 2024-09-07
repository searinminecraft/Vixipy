from flask import Blueprint, g, redirect, render_template, request

from .. import api
from ..core.user import getUserBookmarks

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
