from quart import Blueprint, abort, current_app, render_template, request

from ..core.artwork import getRanking

import logging

rankings = Blueprint("rankings", __name__, url_prefix="/rankings")
log = logging.getLogger("vixipy.routes.ranking")


@rankings.route("/")
async def newestMain():

    mode = request.args.get("mode", "daily")
    date = request.args.get("date", None)
    content = request.args.get("content", None)
    page = int(request.args.get("p", 1))

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

    if current_app.config["nor18"] and mode in (
        "daily_r18",
        "weekly_r18",
    ):
        abort(403)

    if content and content not in ("illust", "manga", "ugoira"):
        return await render_template("error.html", error="Invalid content type"), 400

    data = await getRanking(mode, date, content, page)
    log.debug("Current date: %s (raw: %s)", data.date, data._date)
    log.debug("Next date: %s (raw: %s)", data.nextDate, data._nextDate)
    log.debug("Previous date: %s (raw: %s)", data.prevDate, data._prevDate)
    log.debug("Next: %s - Previous: %s", data.next, data.prev)
    log.debug("Page: %d", data.page)

    return await render_template("rankings.html", data=data)


@rankings.route("/calendar")
async def rankingCalendar():
    return await render_template("error.html", errordesc="Not implemented yet!"), 501
