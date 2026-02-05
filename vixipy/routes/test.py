from quart import Blueprint, render_template
from ..api.handler import pixiv_request

bp = Blueprint("test", __name__, url_prefix="/test")


@bp.route("/exception")
async def raise_exception():
    raise Exception


@bp.route("/")
async def root(): ...


@bp.route("/dialog")
async def dialog():
    return await render_template("test/dialog.html.j2")


@bp.get("/pixiv_exception")
async def pixiv_exception():
    await pixiv_request("/ajax/bogus")
    return ""
