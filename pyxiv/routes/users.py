from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from .. import api
from ..core.user import (
    getUser,
    retrieveUserIllusts,
    getUserBookmarks,
    getUserTopIllusts,
)
from ..classes import User, ArtworkEntry

users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/<int:_id>")
def userPage(_id: int):

    if _id == 0:
        user = User(
            {
                "userId": 0,
                "name": "-----",
                "comment": "This user is hard coded on Vixipy to take place of deleted/unknown users",
                "image": "https://s.pximg.net/common/images/no_profile_s.png",
                "imageBig": "https://s.pximg.net/common/images/no_profile.png",
                "premium": False,
                "background": None,
                "following": 0,
                "mypixivCount": 0,
                "official": True,
            }
        )
        pickup = []
        latestIllust = []
        top = []
        total = 0
    else:
        user = getUser(_id)
        data = api.getUserIllustManga(_id)["body"]
        total = len(data["illusts"]) + len(data["manga"])

        pickup = []
        for x in data["pickup"]:
            # unsupported
            if x["type"] not in ["illust", "manga"]:
                continue
            pickup.append(ArtworkEntry(x))

        top = getUserTopIllusts(_id)

    return render_template(
        "user/main.html", user=user, pickup=pickup, top=top, total=total
    )


@users.route("/<int:_id>/illusts")
def userIllusts(_id: int):

    if _id == 0:
        flash("Invalid user", "error")
        return redirect("/users/0")

    currPage = int(request.args.get("p", 1))

    user = getUser(_id)
    data = api.getUserIllustManga(_id)["body"]["illusts"]

    if len(data) >= 1:
        ids = [int(x) for x in list(data.keys())]

        pages, extra = divmod(len(data), 50)

        if extra > 0:
            pages += 1

        if currPage > pages:
            return render_template("error.html", error="Exceeded maximum pages"), 400

        illusts = retrieveUserIllusts(_id, ids[(50 * currPage) - 50 : 50 * currPage])
    else:
        illusts = []
        pages = 1

    return render_template(
        "user/illusts.html",
        user=user,
        illusts=illusts,
        total=len(data),
        pages=pages,
        canGoNext=(not currPage == pages),
        canGoPrevious=(not currPage == 1),
    )


@users.route("/<int:_id>/manga")
def userManga(_id: int):

    if _id == 0:
        flash("Invalid user", "error")
        return redirect("/users/0")

    currPage = int(request.args.get("p", 1))

    user = getUser(_id)
    data = api.getUserIllustManga(_id)["body"]["manga"]

    if len(data) >= 1:
        ids = [int(x) for x in list(data.keys())]

        pages, extra = divmod(len(data), 50)

        if extra > 0:
            pages += 1

        if currPage > pages:
            return render_template("error.html", error="Exceeded maximum pages"), 400

        illusts = retrieveUserIllusts(_id, ids[(50 * currPage) - 50 : 50 * currPage])
    else:
        illusts = []
        pages = 1

    return render_template(
        "user/manga.html",
        user=user,
        illusts=illusts,
        total=len(data),
        pages=pages,
        canGoNext=(not currPage == pages),
        canGoPrevious=(not currPage == 1),
    )


@users.route("/<int:_id>/bookmarks")
def userBookmarks(_id: int):

    if _id == 0:
        flash("Invalid user", "error")
        return redirect("/users/0")

    page = int(request.args.get("p", 1))

    if current_app.config["authless"]:
        if not g.isAuthorized:
            return render_template("unauthorized.html"), 403

    user = getUser(_id)
    data = getUserBookmarks(_id, offset=(50 * page) - 50)

    pages, extra = divmod(data.total, 50)

    if extra > 0:
        pages += 1

    return render_template(
        "user/bookmarks.html",
        user=user,
        illusts=data.works,
        total=data.total,
        pages=pages,
        canGoNext=(page < pages and not page == pages),
        canGoPrevious=(not page == 1),
    )
