from quart import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for
)

from asyncio import gather
from ..api import get_user, get_user_profile_top, get_user_illusts, get_user_bookmarks
from ..decorators import tokenless_require_login

bp = Blueprint("users", __name__)

@bp.get("/users/<int:user>")
async def user_profile(user: int):
    data, top = await gather(
        get_user(user, True),
        get_user_profile_top(user)
    )

    return await render_template("users/top.html", data=data, top=top)

@bp.get("/users/<int:user>/illustrations")
async def user_illusts(user: int):
    data, il = await gather(
        get_user(user, True),
        get_user_illusts(user, page=int(request.args.get("p", 1)))
    )

    return await render_template("users/illust.html", data=data, il=il)

@bp.get("/users/<int:user>/manga")
async def user_manga(user: int):
    data, il = await gather(
        get_user(user, True),
        get_user_illusts(user, content_type="manga", page=int(request.args.get("p", 1)))
    )

    return await render_template("users/manga.html", data=data, il=il)


@bp.get("/users/<int:user>/bookmarks")
@tokenless_require_login
async def user_bookmarks(user: int):
    data, bkdata = await gather(
        get_user(user, True),
        get_user_bookmarks(user, int(request.args.get("p", 1)), request.args.get("tag", ""))
    )

    pages, y = divmod(bkdata[0], 48)
    if y > 0:
        pages += 1

    return await render_template("users/bookmarks.html", data=data, il=bkdata[1], pages=pages)


@bp.get("/u/<int:user>")
async def pixivcompat_user(user: int):
    return redirect(url_for("users.user_profile", user=user))