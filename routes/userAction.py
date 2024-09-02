from flask import Blueprint, redirect, request

import api

userAction = Blueprint("userAction", __name__, url_prefix="/self")

@userAction.route("/addbookmark/<int:_id>")
def addBookmark(_id: int):

    api.pixivPostReq("/ajax/illusts/bookmarks/add", jsonPayload={"illust_id": str(_id), "restrict": 0, "comment": "", "tags": []})

    return redirect(request.args["r"])

@userAction.route("/removebookmark/<int:_id>")
def deleteBookmark(_id: int):

    api.pixivPostReq("/ajax/illusts/bookmarks/delete", rawPayload=f"bookmark_id={_id}")

    return redirect(request.args["r"])
