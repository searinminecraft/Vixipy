from quart import (
    Blueprint,
    abort,
    current_app,
    g,
    render_template,
    request,
    url_for,
    redirect,
)
from quart_rate_limiter import RateLimit, limit_blueprint, timedelta
from quart_babel import _

from ..core.artwork import getRanking
from ..core.user import getUserSettingsState
from ..utils.converters import makeProxy

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import logging

rankings = Blueprint("rankings", __name__, url_prefix="/rankings")
log = logging.getLogger("vixipy.routes.ranking")
limit_blueprint(
    rankings,
    limits=[RateLimit(1, timedelta(seconds=5)), RateLimit(30, timedelta(minutes=2))],
)


async def getCalendar(mode: str = "daily", date: int = None):
    path = f"/ranking_log.php?mode={mode}"

    if date:
        path += f"&date={date}"

    req = await current_app.pixivApi.get(path)
    req.raise_for_status()

    r = await req.text()

    s = BeautifulSoup(r, "html.parser")

    res = []
    weeks = s.find_all("tr")
    for week in weeks:
        for t in week.find_all("td"):
            attrs = t.get_attribute_list("class")
            isActive = "active" in attrs
            lnk = None
            img = None
            day = None
            date = None
            image = None

            da = t.find("span", class_="day")
            dt = t.find("span", class_="date")
            l = t.find("a")
            if l:
                lnk = l.get("href")
                img = makeProxy(l.find("img").get("data-src"))
            if da:
                day = da.text
                match day:
                    case "Mon":
                        date = _("Mon")
                    case "Tue":
                        date = _("Tue")
                    case "Wed":
                        date = _("Wed")
                    case "Thu":
                        date = _("Thu")
                    case "Fri":
                        date = _("Fri")
                    case "Sat":
                        date = _("Sat")
                    case "Sun":
                        date = _("Sun")
            if dt:
                date = dt.text
            res.append(
                {
                    "active": isActive,
                    "link": lnk,
                    "day": day,
                    "date": date,
                    "image": img,
                }
            )

    return res


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
    mode = request.args.get("mode", "daily")
    date = request.args.get("date", None)
    if date:
        date = date.replace("-", "")
        sel = datetime.strptime(date, "%Y%m")
    else:
        date = datetime.now()
        sel = date

    data = await getCalendar(mode, date)
    ar = request.args.copy()
    if "date" in ar:
        ar.pop("date")

    current = datetime.now()
    if sel.month == 2:
        prev = sel - timedelta(weeks=3)
    else:
        prev = sel - timedelta(weeks=4)
    next_ = sel + timedelta(weeks=5)
    print(prev, next_)

    prevUrl = url_for(
        "rankings.rankingCalendar",
        **ar,
        date=f"{prev.year}{prev.month if prev.month >= 10 else f'0{prev.month}'}",
    )
    nextUrl = url_for(
        "rankings.rankingCalendar",
        **ar,
        date=f"{next_.year}{next_.month if next_.month >= 10 else f'0{next_.month}'}",
    )
    return await render_template(
        "rankingCalendar.html", data=data, date=sel, prev=prevUrl, next=nextUrl
    )


@rankings.route("/ranking.php")
async def rankingRedir():
    return redirect(url_for("rankings.rankingsMain", **request.args))
