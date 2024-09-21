from flask import Blueprint, g, redirect, render_template, request, url_for

from ..core.search import searchArtwork, getTagInfo

tag = Blueprint("tag", __name__, url_prefix="/tag")


@tag.route("/<name>")
def tagMain(name):

    args = request.args.copy()

    data = searchArtwork(name, **args)
    tagInfo = getTagInfo(name)

    g.tag = name

    try:
        currPage = args.pop("p")
    except KeyError:
        currPage = 1

    if int(currPage) > data.lastPage:
        return (
            render_template(
                "error.html",
                error=f"Exceeded maximum pages ({currPage} > {data.lastPage}). Did you really try?",
            ),
            400,
        )

    if len(args) > 0:
        useSym = "&"
    else:
        useSym = "?"

    path = url_for("tag.tagMain", name=name, **args)

    return render_template(
        "tag.html",
        data=data,
        tagInfo=tagInfo,
        currPage=currPage,
        path=path,
        useSym=useSym,
    )


@tag.post("/")
def handleSearchBox():
    return redirect(url_for("tag.tagMain", name=request.form["tag"]))
