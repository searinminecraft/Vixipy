from quart import Blueprint, abort, request, render_template, url_for

from ..lib.scrapes import get_ranking_calendar

from datetime import datetime, timedelta

bp = Blueprint("rankings", __name__)


@bp.route("/rankings/calendar")
async def ranking_calendar():
    date = request.args.get("date", None)
    mode = request.args.get("mode", "daily")

    if date:
        date = date.replace("-", "")
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
        current=current,
        nextUrl=nextUrl,
        prevUrl=prevUrl,
    )
