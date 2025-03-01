from quart import Blueprint, abort, redirect, render_template, request, url_for
from urllib.parse import urlparse
import logging

bp = Blueprint("pixivCompat", __name__)
log = logging.getLogger("vixipy.routes.pixivCompat")


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
                "subscribestar.adult",
                "gumroad.com",
            )
        ]
    )

    return await render_template(
        "leave.html", dest=dest, showSensitiveNotice=showSensitiveNotice
    )


@bp.get("/member_illust.php")
async def member_illust():
    args = request.args

    # currently only comment_chk is known

    match args["mode"]:
        case "comment_chk":
            return redirect(
                url_for("artworks.artworkComments", _id=args["illust_id"]), code=308
            )
        case _:
            log.warning(
                "member_illust.php: Unknown mode %s, stubbing!", args.get("mode")
            )
            abort(400)


@bp.get("/messages.php")
async def messages():
    if thread_id := request.args.get("thread_id"):
        return redirect(
            url_for("messages.messageThread", thread_id=thread_id), code=308
        )
    else:
        return redirect(
            url_for("messages.messagesMain"), code=308
        )
