from __future__ import annotations

from quart import Blueprint, current_app, abort, request, render_template, url_for
from quart_rate_limiter import RateLimit, rate_limit, timedelta

from ..lib.scrapes import get_ranking_calendar
from ..api.ranking import get_ranking

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from werkzeug.datastructures import MultiDict

bp = Blueprint("rankings", __name__)


@bp.route("/rankings")
@rate_limit(
    limits=[RateLimit(2, timedelta(seconds=1)), RateLimit(10, timedelta(seconds=30))]
)
async def main():

    mode: str = request.args.get("mode", "daily") or "daily"
    date: str = request.args.get("date")
    content: str = request.args.get("content", "illust") or "illust"
    page: int = int(request.args.get("p", 1)) or 1

    if date:
        # For specified date in options
        date = date.replace("-", "")

    if mode not in (
        "daily",
        "weekly",
        "monthly",
        "rookie",
        "male",
        "female",
        "original",
        "daily_ai",
        "daily_r18_ai",
        "daily_r18",
        "weekly_r18",
        "male_r18",
        "female_r18",
    ):
        abort(400)

    if content not in ("illust", "manga", "ugoira"):
        abort(400)

    if (
        current_app.config["NO_SENSITIVE"] or current_app.config["NO_R18"]
    ) and mode in ("daily_r18", "daily_r18_ai", "weekly_r18", "male_r18", "female_r18"):
        abort(403)

    #  content param is incompatible with some modes
    if mode in ("daily_ai", "daily_r18_ai", "original"):
        content = None

    data = await get_ranking(mode, date, content, page)

    return await render_template("rankings/main.html", data=data)


@bp.route("/rankings/calendar")
@rate_limit(1, timedelta(seconds=2))
async def ranking_calendar():
    date = request.args.get("date", None)
    mode = request.args.get("mode", "daily")

    if date:
        date = date.replace("-", "")[:6]
        sel = datetime.strptime(date, "%Y%m")
    else:
        date = datetime.now()
        sel = date

    if mode not in (
        "daily",
        "weekly",
        "monthly",
        "rookie",
        "male",
        "female",
        "original",
        "daily_ai",
        "daily_r18_ai",
        "daily_r18",
        "weekly_r18",
        "male_r18",
        "female_r18",
    ):
        abort(400)

    if (
        current_app.config["NO_SENSITIVE"] or current_app.config["NO_R18"]
    ) and mode in ("daily_r18", "daily_r18_ai", "weekly_r18", "male_r18", "female_r18"):
        abort(403)

    data = await get_ranking_calendar(date, mode)

    ar = request.args.copy()
    if "date" in ar:
        ar.pop("date")

    current = datetime.now()
    if sel.month == 2:
        prev = sel - timedelta(weeks=3)
    else:
        prev = sel - timedelta(weeks=4)
    next_ = sel + timedelta(weeks=5)

    prevUrl = url_for(
        "rankings.ranking_calendar",
        **ar,
        date=f"{prev.year}{prev.month if prev.month >= 10 else f'0{prev.month}'}",
    )
    nextUrl = url_for(
        "rankings.ranking_calendar",
        **ar,
        date=f"{next_.year}{next_.month if next_.month >= 10 else f'0{next_.month}'}",
    )

    return await render_template(
        "rankings/calendar.html",
        data=data,
        current=sel,
        nextUrl=nextUrl,
        prevUrl=prevUrl,
    )
