from quart import Blueprint, abort, current_app, g, render_template, request, url_for
from quart_rate_limiter import RateLimit, limit_blueprint, timedelta

from ..core.artwork import getRanking
from ..core.user import getUserSettingsState

import logging

rankings = Blueprint("rankings", __name__, url_prefix="/rankings")
log = logging.getLogger("vixipy.routes.ranking")
limit_blueprint(
    rankings,
    limits=[RateLimit(1, timedelta(seconds=5)), RateLimit(30, timedelta(minutes=2))],
)


@rankings.route("/")
async def rankingsMain():

    mode: str = request.args.get("mode", "daily")
    date: str = request.args.get("date", None)
    content: str = request.args.get("content", None)
    page: int = int(request.args.get("p", 1))

    if date:
        # For specified date in options
        date = date.replace("-", "")

    if mode not in (
        "daily",
        "daily_ai",
        "weekly",
        "monthly",
        "rookie",
        "original",
        "daily_r18",
        "weekly_r18",
    ):
        return await render_template("error.html", errordesc="Invalid mode"), 400

    if mode in (
        "daily_r18",
        "weekly_r18",
    ):
        if not g.isAuthorized:
            abort(401)
        elif current_app.config["nor18"]:
            abort(403)

    if content and content not in ("illust", "manga", "ugoira"):
        return await render_template("error.html", error="Invalid content type"), 400

    if g.isAuthorized:
        xRestrictEnabled = (await getUserSettingsState()).xRestrictEnabled
    else:
        xRestrictEnabled = False

    newargs = request.args.copy()
    # content is incompatible with these modes
    if mode in ("daily_ai", "original"):
        newargs.pop("mode")
        content = None

    data = await getRanking(mode, date, content, page)
    log.debug("Current date: %s (raw: %s)", data.date, data._date)
    log.debug("Next date: %s (raw: %s)", data.nextDate, data._nextDate)
    log.debug("Previous date: %s (raw: %s)", data.prevDate, data._prevDate)
    log.debug("Next: %s - Previous: %s", data.next, data.prev)
    log.debug("Page: %d", data.page)

    if "p" in newargs:
        newargs.pop("p")
    if data.prev:
        prevPage = url_for("rankings.rankingsMain", **newargs, p=data.prev)
        log.debug(prevPage)
    else:
        prevPage = None
    if data.next:
        nextPage = url_for("rankings.rankingsMain", **newargs, p=data.next)
        log.debug(nextPage)
    else:
        nextPage = None

    return await render_template(
        "rankings.html",
        data=data,
        prevPage=prevPage,
        nextPage=nextPage,
        xRestrictEnabled=xRestrictEnabled,
    )


@rankings.route("/calendar")
async def rankingCalendar():
    return await render_template("error.html", errordesc="Not implemented yet!"), 501
