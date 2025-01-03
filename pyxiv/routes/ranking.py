from quart import Blueprint, abort, current_app, render_template, request

from ..api import PixivError
from ..core.artwork import getRanking

from datetime import datetime

rankings = Blueprint("rankings", __name__, url_prefix="/rankings")


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

    return await render_template("rankings.html", data=data)
