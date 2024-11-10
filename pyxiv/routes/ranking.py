from flask import Blueprint, render_template, request

from ..api import PixivError
from ..core.artwork import getRanking

from datetime import datetime

rankings = Blueprint("rankings", __name__, url_prefix="/rankings")


@rankings.route("/")
def newestMain():

    mode = request.args.get("mode", "daily")
    date = request.args.get("date")
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
        return render_template("error.html", error="Invalid mode"), 400

    if content and content not in ("illust", "manga", "ugoira"):
        return render_template("error.html", error="Invalid content type"), 400

    if not date:
        try:
            data = getRanking(
                mode, int(datetime.now().strftime("%Y%m%d")) - 1, content, page
            )
        except PixivError:
            data = getRanking(
                mode, int(datetime.now().strftime("%Y%m%d")) - 2, content, page
            )
    else:
        data = getRanking(mode, date, content, page)

    return render_template("rankings.html", data=data)
