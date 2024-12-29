from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
    abort,
)
from ..core.search import searchArtwork, getTagInfo

tag = Blueprint("tag", __name__, url_prefix="/tag")


@tag.route("/<name>")
def tagMain(name):

    args = request.args.copy()
    actual = request.args.copy()

    if args.get("mode", "safe") == "r18" and current_app.config["nor18"]:
        abort(400)
    
    if args.get("overridepagecount"):
        overridepagecount = args.pop("overridepagecount") == "on"
    else:
        overridepagecount = False

    try:
        data = searchArtwork(name, **args)
    except TypeError:
        abort(400)

    tagInfo = getTagInfo(name)

    g.tag = name

    try:
        currPage = actual.pop("p")
    except KeyError:
        currPage = 1

    if int(currPage) > data.lastPage and not overridepagecount:
        return (
            render_template(
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

    return render_template(
        "tag.html",
        data=data,
        tagInfo=tagInfo,
        currPage=currPage,
        path=path,
        useSym=useSym,
        gobeyond=overridepagecount
    )


@tag.post("/")
def handleSearchBox():
    return redirect(url_for("tag.tagMain", name=request.form["tag"]))
