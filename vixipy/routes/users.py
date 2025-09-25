from quart import Blueprint, abort, g, redirect, render_template, request, url_for
from quart_rate_limiter import timedelta, rate_limit

from asyncio import gather
from ..api import (
    get_user,
    get_user_profile_top,
    get_user_illusts,
    get_user_bookmarks,
    get_user_followers,
    get_user_following,
    get_user_mypixiv,
    pixiv_request,
)
from ..decorators import tokenless_require_login, require_login
from ..filters import filter_from_prefs as ff
from ..types import NovelEntry

bp = Blueprint("users", __name__)


@bp.get("/users/<int:user>")
@rate_limit(1, timedelta(seconds=5))
async def user_profile(user: int):
    data, top = await gather(get_user(user, True), get_user_profile_top(user))

    return await render_template("users/top.html", data=data, top=ff(top))


@bp.get("/users/<int:user>/illustrations")
@rate_limit(1, timedelta(seconds=1))
async def user_illusts(user: int):
    data, il = await gather(
        get_user(user, True), get_user_illusts(user, page=int(request.args.get("p", 1)))
    )

    il.illusts = ff(il.illusts)

    return await render_template("users/illust.html", data=data, il=il)


@bp.get("/users/<int:user>/manga")
@rate_limit(2, timedelta(seconds=3))
async def user_manga(user: int):
    data, il = await gather(
        get_user(user, True),
        get_user_illusts(
            user, content_type="manga", page=int(request.args.get("p", 1))
        ),
    )

    il.illusts = ff(il.illusts)

    return await render_template("users/manga.html", data=data, il=il)


@bp.get("/users/<int:user>/bookmarks")
@rate_limit(2, timedelta(seconds=3))
@tokenless_require_login
async def user_bookmarks(user: int):
    data, bkdata = await gather(
        get_user(user, True),
        get_user_bookmarks(
            user, int(request.args.get("p", 1)), request.args.get("tag", "")
        ),
    )

    pages, y = divmod(bkdata[0], 48)
    if y > 0:
        pages += 1

    return await render_template(
        "users/bookmarks.html", data=data, il=ff(bkdata[1]), pages=pages
    )


@bp.get("/users/<int:user>/novels")
@rate_limit(2, timedelta(seconds=3))
async def user_novels(user: int):
    data, cts = await gather(
        get_user(user, True), pixiv_request(f"/ajax/user/{user}/profile/all")
    )

    p = int(request.args.get("p", 1))

    if len(cts["novels"]) > 0:
        novel_ids = [int(x) for x in cts["novels"].keys()]
        to_get = novel_ids[(30 * p) - 30 : 30 * p]

        ndata = await pixiv_request(
            f"/ajax/user/{user}/profile/novels", params=[("ids[]", x) for x in to_get]
        )
        novels = [NovelEntry(x) for x in ndata["works"].values()]

        pages, _ = divmod(len(novels), 30)
        if _ > 0:
            pages += 1
    else:
        novels = []
        pages = 1

    return await render_template(
        "users/novels.html", data=data, novels=ff(novels), pages=pages
    )


@bp.route("/users/<int:user>/following")
@tokenless_require_login
async def following(user: int):
    user, data = await gather(
        get_user(user),
        get_user_following(
            user,
            int(request.args.get("p", 1)),
            request.args.get("rest", "show"),
            int(request.args.get("acceptingRequests", 0)),
        ),
    )

    return await render_template("users/follow/following.html", user=user, data=data)


@bp.route("/users/<int:user>/followers")
@tokenless_require_login
async def followers(user: int):
    if g.current_user.id != user:
        abort(400)

    user, data = await gather(
        get_user(user), get_user_followers(user, int(request.args.get("p", 1)))
    )

    return await render_template("users/follow/followers.html", user=user, data=data)


@bp.route("/users/<int:user>/mypixiv")
@tokenless_require_login
async def mypixiv(user: int):

    user, data = await gather(
        get_user(user), get_user_mypixiv(user, int(request.args.get("p", 1)))
    )

    return await render_template("users/follow/mypixiv.html", user=user, data=data)


@bp.get("/u/<int:user>")
async def pixivcompat_user(user: int):
    return redirect(url_for("users.user_profile", user=user))


@bp.get("/self/actions")
async def user_dashboard():
    return await render_template("users/dashboard.html")
