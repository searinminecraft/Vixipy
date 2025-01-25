from quart import Blueprint, abort, redirect, render_template, request, url_for
from urllib.parse import urlparse

bp = Blueprint("pixivCompat", __name__)


@bp.route("/new_illust.php")
async def newIllustRedirect():
    return redirect(url_for("newest.newestMain", **request.args), code=308)


@bp.route("/new_illust_r18.php")
async def newIllustR18Redirect():
    return redirect(url_for("newest.newestMain", **request.args, r18="true"), code=308)


@bp.route("/ranking.php")
async def rankingRedirect():
    return redirect(url_for("rankings.rankingsMain", **request.args), code=308)


@bp.route("/ranking_log.php")
async def rankingCalendarRedirect():
    return redirect(url_for("rankings.rankingCalendar", **request.args), code=308)


@bp.get("/jump.php")
async def pixivRedir():
    try:
        if request.args.get("url"):
            # /jump.php?url=https://kita.codeberg.page
            dest = request.args["url"]
        else:
            # /jump.php?https://kita.codeberg.page
            dest = list(request.args.keys())[0]
    except (IndexError, KeyError):
        abort(400)

    domain = urlparse(dest).netloc

    showSensitiveNotice = any(
        [
            domain.__contains__(x)
            for x in (
                "fanbox.cc",
                "patreon.com",
            )
        ]
    )

    return await render_template(
        "leave.html", dest=dest, showSensitiveNotice=showSensitiveNotice
    )
