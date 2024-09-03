from flask import Blueprint, g, redirect, request

from .. import api

userAction = Blueprint("userAction", __name__, url_prefix="/self")


@userAction.route("/")
def redirectToSelf():

    return redirect(f"/users/{g.curruserId}")


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
