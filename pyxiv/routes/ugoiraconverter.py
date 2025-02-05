from quart import Blueprint, redirect, request, abort, render_template, url_for, flash
from ..core.artwork import getArtwork
from ..api import PixivError
from werkzeug.exceptions import NotFound

from quart_babel import _

bp = Blueprint("ugoiraconverter", __name__)


@bp.route("/ugoira-convert/<int:_id>")
async def converterMain(_id: int):
    try:
        data = await getArtwork(_id)
        if not data.isUgoira:
            await flash(_("The ID you specified is not an ugoira."), "error")
            return redirect(url_for("ugoiraconverter.ugoiraMain"), code=303)
    except NotFound:
        await flash(_("Illustration not found"), "error")
        return redirect(url_for("ugoiraconverter.ugoiraMain"), code=303)
    except PixivError as e:
        await flash(_("pixiv returned an error: %(error)s", error=str(e)), "error")
        return redirect(url_for("ugoiraconverter.ugoiraMain"), code=303)
    except Exception as e:
        await flash(str(e), "error")
        return redirect(url_for("ugoiraconverter.ugoiraMain"), code=303)

    return await render_template("ugoiraConverter/converter.html", data=data)


@bp.post("/ugoira-convert")
async def handler():
    f = await request.form
    return redirect(url_for("ugoiraconverter.converterMain", _id=f["id"]))


@bp.route("/ugoira-convert")
async def ugoiraMain():
    return await render_template("ugoiraConverter/index.html")
