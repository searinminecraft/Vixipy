from flask import Blueprint, g, redirect, render_template, request, url_for

from ..core.search import searchArtwork, getTagInfo

tag = Blueprint("tag", __name__, url_prefix="/tag")


@tag.route("/<name>")
def tagMain(name):
    data = searchArtwork(name, **request.args)
    tagInfo = getTagInfo(name)

    return render_template("tag.html", data=data, tagInfo=tagInfo)


@tag.post("/")
def handleSearchBox():
    return redirect(url_for("tag.tagMain", name=request.form["tag"]))
