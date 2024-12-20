from flask import (
    Blueprint,
    abort,
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
    getUserFollowing,
    getUserFollowers,
)
from ..core.artwork import getFrequentTags
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
                "isFollowed": False,
                "commentHtml": "",
            }
        )
        pickup = []
        latestIllust = []
        top = []
        frequent = []
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
        frequent = getFrequentTags([x._id for x in top]) if len(top) > 0 else []

    return render_template(
        "user/main.html",
        user=user,
        pickup=pickup,
        top=top,
        total=total,
        frequent=frequent,
    )


@users.route("/<int:_id>/illusts")
def userIllusts(_id: int):

    if _id == 0:
        flash(_("Invalid user"), "error")
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

        offset = ids[(50 * currPage) - 50 : 50 * currPage]
        illusts = retrieveUserIllusts(_id, offset)
        frequent = getFrequentTags(offset)
    else:
        illusts = []
        frequent = []
        pages = 1

    return render_template(
        "user/illusts.html",
        user=user,
        illusts=illusts,
        total=len(data),
        pages=pages,
        frequent=frequent,
        canGoNext=(not currPage == pages),
        canGoPrevious=(not currPage == 1),
    )


@users.route("/<int:_id>/manga")
def userManga(_id: int):

    if _id == 0:
        flash(_("Invalid user"), "error")
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

        offset = ids[(50 * currPage) - 50 : 50 * currPage]
        illusts = retrieveUserIllusts(_id, offset)
        frequent = getFrequentTags(offset)
    else:
        illusts = []
        frequent = []
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
        flash(_("Invalid user"), "error")
        return redirect("/users/0")

    page = int(request.args.get("p", 1))

    if current_app.config["authless"]:
        if not g.isAuthorized:
            abort(401)

    user = getUser(_id)
    data = getUserBookmarks(_id, offset=(50 * page) - 50)
    if len(data) > 0:
        frequent = getFrequentTags([x._id for x in data.works])
    else:
        frequent = []

    pages, extra = divmod(data.total, 50)

    if extra > 0:
        pages += 1

    return render_template(
        "user/bookmarks.html",
        user=user,
        illusts=data.works,
        total=data.total,
        pages=pages,
        frequent=frequent,
        canGoNext=(page < pages and not page == pages),
        canGoPrevious=(not page == 1),
    )


@users.route("/<int:_id>/following")
def following(_id: int):

    if _id == 0:
        flash(_("Invalid user"), "error")
        return redirect("/users/0")

    if current_app.config["authless"]:
        if not g.isAuthorized:
            abort(401)

    currPage = int(request.args.get("p", 1))

    total, data = getUserFollowing(_id)
    user = getUser(_id)

    pages, extra = divmod(total, 30)
    if extra > 0:
        pages += 1

    _, data = getUserFollowing(_id, offset=(30 * currPage) - 30)

    return render_template(
        "user/follows.html",
        total=total,
        pages=pages,
        data=data,
        mode="following",
        user=user,
        canGoNext=(currPage < pages and not currPage == pages),
        canGoPrevious=(),
    )


@users.route("/<int:_id>/followers")
def followers(_id: int):

    if current_app.config["authless"]:
        if not g.isAuthorized:
            abort(401)

    if _id == 0:
        flash(_("Invalid user"), "error")
        return redirect("/users/0")

    currPage = int(request.args.get("p", 1))

    try:
        total, data = getUserFollowers(_id)
    except api.PixivError:
        flash(_("Not authorized."), "error")
        return redirect(f"/users/{_id}/following")

    user = getUser(_id)

    pages, extra = divmod(total, 30)
    if extra > 0:
        pages += 1

    _, data = getUserFollowers(_id, offset=(30 * currPage) - 30)

    return render_template(
        "user/follows.html",
        total=total,
        pages=pages,
        data=data,
        mode="follows",
        user=user,
        canGoNext=(currPage < pages and not currPage == pages),
        canGoPrevious=(),
    )
