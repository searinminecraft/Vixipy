from quart import Blueprint, request, render_template

from ..core.discovery import getNewestArtworks

newest = Blueprint("newest", __name__, url_prefix="/newest")


@newest.route("/")
async def newestMain():

    _type = request.args.get("type", "illust")
    r18 = request.args.get("r18", "false") == "true"

    data = await getNewestArtworks(_type=_type, r18=r18)

    return await render_template("newest.html", data=data)
