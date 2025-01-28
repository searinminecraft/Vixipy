from quart import Blueprint, render_template
from ..core.news import getNewsEntry

bp = Blueprint("news", __name__, url_prefix="/news")

@bp.route("/<int:id>")
async def getEntry(id: int):
    data = await getNewsEntry(id)
    return await render_template("news/entry.html", data=data)
