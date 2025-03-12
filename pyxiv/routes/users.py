from quart import (
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
from quart_rate_limiter import RateLimit, limit_blueprint, timedelta
from asyncio import gather

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
limit_blueprint(
    users,
    limits=[RateLimit(1, timedelta(seconds=2)), RateLimit(10, timedelta(minutes=1))],
)


@users.route("/<int:_id>")
async def userPage(_id: int):

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
                "socials": {}
            }
        )
        pickup = []
        latestIllust = []
        top = []
        frequent = []
        total = 0
    else:
        user, data, top = await gather(
            getUser(_id),
            api.getUserIllustManga(_id),
            getUserTopIllusts(_id),
        )
        data = data["body"]

        if any([x.xRestrict for x in top]):
            if not bool(int(request.cookies.get("VixipyConsentSensitiveContent", 0))):
                return await render_template(
                    "sensitivityWarning.html", dest=request.full_path
                )

        total = len(data["illusts"]) + len(data["manga"])

        pickup = []
        for x in data["pickup"]:
            # unsupported
            if x["type"] not in ["illust", "manga"]:
                continue
            pickup.append(ArtworkEntry(x))

        frequent = await getFrequentTags([x._id for x in top]) if len(top) > 0 else []

    return await render_template(
        "user/main.html",
        user=user,
        pickup=pickup,
        top=top,
        total=total,
        frequent=frequent,
    )


@users.route("/<int:_id>/illusts")
async def userIllusts(_id: int):

    if _id == 0:
        await flash(_("Invalid user"), "error")
        return redirect("/users/0")

    currPage = int(request.args.get("p", 1))

    user, data = await gather(
        getUser(_id),
        api.getUserIllustManga(_id),
    )
    data = data["body"]["illusts"]

    if len(data) >= 1:
        ids = [int(x) for x in list(data.keys())]

        pages, extra = divmod(len(data), 50)

        if extra > 0:
            pages += 1

        if currPage > pages:
            return render_template("error.html", error="Exceeded maximum pages"), 400

        offset = ids[(50 * currPage) - 50 : 50 * currPage]
        illusts, frequent = await gather(
            retrieveUserIllusts(_id, offset),
            getFrequentTags(offset),
        )
        if any([x.xRestrict for x in illusts]):
            if not bool(int(request.cookies.get("VixipyConsentSensitiveContent", 0))):
                return await render_template(
                    "sensitivityWarning.html", dest=request.full_path
                )

    else:
        illusts = []
        frequent = []
        pages = 1

    return await render_template(
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
async def userManga(_id: int):

    if _id == 0:
        await flash(_("Invalid user"), "error")
        return redirect("/users/0")

    currPage = int(request.args.get("p", 1))

    user, data = await gather(
        getUser(_id),
        api.getUserIllustManga(_id),
    )
    data = data["body"]["manga"]

    if len(data) >= 1:
        ids = [int(x) for x in list(data.keys())]

        pages, extra = divmod(len(data), 50)

        if extra > 0:
            pages += 1

        if currPage > pages:
            return (
                await render_template("error.html", error="Exceeded maximum pages"),
                400,
            )

        offset = ids[(50 * currPage) - 50 : 50 * currPage]
        illusts, frequent = await gather(
            retrieveUserIllusts(_id, offset),
            getFrequentTags(offset),
        )
        if any([x.xRestrict for x in illusts]):
            if not bool(int(request.cookies.get("VixipyConsentSensitiveContent", 0))):
                return await render_template(
                    "sensitivityWarning.html", dest=request.full_path
                )

    else:
        illusts = []
        frequent = []
        pages = 1

    return await render_template(
        "user/manga.html",
        user=user,
        illusts=illusts,
        total=len(data),
        pages=pages,
        canGoNext=(not currPage == pages),
        canGoPrevious=(not currPage == 1),
    )


@users.route("/<int:_id>/bookmarks")
async def userBookmarks(_id: int):

    if _id == 0:
        await flash(_("Invalid user"), "error")
        return redirect("/users/0")

    page = int(request.args.get("p", 1))

    if current_app.config["authless"]:
        if not g.isAuthorized:
            abort(401)

    user, data = await gather(
        getUser(_id),
        getUserBookmarks(_id, offset=(50 * page) - 50),
    )
    if any([x.xRestrict for x in data.works]):
        if not bool(int(request.cookies.get("VixipyConsentSensitiveContent", 0))):
            return await render_template(
                "sensitivityWarning.html", dest=request.full_path
            )

    if len(data) > 0:
        frequent = await getFrequentTags([x._id for x in data.works])
    else:
        frequent = []

    pages, extra = divmod(data.total, 50)

    if extra > 0:
        pages += 1

    return await render_template(
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
async def following(_id: int):

    if _id == 0:
        await flash(_("Invalid user"), "error")
        return redirect("/users/0")

    if current_app.config["authless"]:
        if not g.isAuthorized:
            abort(401)

    currPage = int(request.args.get("p", 1))

    _data, user, data = await gather(
        getUserFollowing(_id),
        getUser(_id),
        getUserFollowing(_id, offset=(30 * currPage) - 30),
    )

    total = _data[0]
    pages, extra = divmod(total, 30)
    if extra > 0:
        pages += 1

    return await render_template(
        "user/follows.html",
        total=total,
        pages=pages,
        data=data[1],
        mode="following",
        user=user,
        canGoNext=(currPage < pages and not currPage == pages),
        canGoPrevious=(),
    )


@users.route("/<int:_id>/followers")
async def followers(_id: int):

    if current_app.config["authless"]:
        if not g.isAuthorized:
            abort(401)

    if _id == 0:
        await flash(_("Invalid user"), "error")
        return await redirect("/users/0")

    currPage = int(request.args.get("p", 1))

    _data, user, data = await gather(
        getUserFollowers(_id),
        getUser(_id),
        getUserFollowers(_id, offset=(30 * currPage) - 30),
    )

    total = _data[0]
    pages, extra = divmod(total, 30)
    if extra > 0:
        pages += 1

    return await render_template(
        "user/follows.html",
        total=total,
        pages=pages,
        data=data[1],
        mode="follows",
        user=user,
        canGoNext=(currPage < pages and not currPage == pages),
        canGoPrevious=(),
    )
