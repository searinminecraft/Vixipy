from quart import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
    abort,
)
from quart_rate_limiter import RateLimit, limit_blueprint, timedelta
from ..core.search import searchArtwork, getTagInfo
from asyncio import gather

tag = Blueprint("tag", __name__, url_prefix="/tag")
limit_blueprint(
    tag,
    limits=[RateLimit(1, timedelta(seconds=3)), RateLimit(15, timedelta(minutes=1))],
)


@tag.route("/<name>")
async def tagMain(name):

    args = request.args.copy()
    actual = request.args.copy()

    if args.get("mode", "safe") == "r18" and current_app.config["nor18"]:
        abort(400)

    if args.get("overridepagecount"):
        overridepagecount = args.pop("overridepagecount") == "on"
    else:
        overridepagecount = False

    try:
        data, tagInfo = await gather(searchArtwork(name, **args), getTagInfo(name))
    except Exception:
        abort(400)

    g.tag = name

    try:
        currPage = actual.pop("p")
    except KeyError:
        currPage = 1

    if int(currPage) > data.lastPage and not overridepagecount:
        return (
            await render_template(
                "error.html",
                errordesc=f"Exceeded maximum pages ({currPage} > {data.lastPage}). If you want to override this, turn on 'Go beyond last page' on the advanced search options.",
            ),
            400,
        )

    if len(actual) > 0:
        useSym = "&"
    else:
        useSym = "?"

    path = url_for("tag.tagMain", name=name, **actual)

    return await render_template(
        "tag.html",
        data=data,
        tagInfo=tagInfo,
        currPage=currPage,
        path=path,
        useSym=useSym,
        gobeyond=overridepagecount,
    )


@tag.post("/")
async def handleSearchBox():
    f = await request.form
    return redirect(url_for("tag.tagMain", name=f["tag"]))
