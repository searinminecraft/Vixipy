from quart import Blueprint, render_template, url_for, redirect, request
from ..api.follow import get_latest_works_from_following, get_latest_novels_from_following

bp = Blueprint("follow", __name__)

@bp.route("/follow/new")
async def bookmark_new_illust():
    data, is_last_page = await get_latest_works_from_following(
        request.args.get("p", 1, type=int),
        request.args.get("mode", "all"),
    )
    return await render_template("follow/users/illust.html.j2", data=data, is_last=is_last_page)

@bp.route("/follow/novel/new")
async def novel_bookmark_new():
    data, is_last_page = await get_latest_novels_from_following(
        request.args.get("p", 1, type=int),
        request.args.get("mode", "all"),
    )
    return await render_template("follow/users/novel.html.j2", data=data, is_last=is_last_page)

@bp.route("/bookmark_new_illust.php")
def legacy_redirect():
    return redirect(url_for("follow.bookmark_new_illust"), code=308)

@bp.route("/novel/bookmark_new.php")
def legacy_bookmark_redirect():
    return redirect(url_for("follow.novel_bookmark_new"), code=308)


@bp.route("/bookmark_new_illust_r18.php")
def legacy_redirect_r18():
    return redirect(url_for("follow.bookmark_new_illust", mode='r18'), code=308)

@bp.route("/novel/bookmark_new_r18.php")
def legacy_bookmark_redirect_r18():
    return redirect(url_for("follow.novel_bookmark_new", mode='r18'), code=308)
