from quart import Blueprint, redirect, request, abort, render_template, url_for
from ..core.artwork import getArtwork

bp = Blueprint("ugoiraconverter", __name__)


@bp.route("/ugoira-convert/<int:_id>")
async def converterMain(_id: int):
    data = await getArtwork(_id)
    if not data.isUgoira:
        abort(400)

    return await render_template("ugoiraConverter/converter.html", data=data)


@bp.post("/ugoira-convert")
async def handler():
    f = await request.form
    return redirect(url_for("ugoiraconverter.converterMain", _id=f["id"]))


@bp.route("/ugoira-convert")
async def ugoiraMain():
    return await render_template("ugoiraConverter/index.html")
