from quart import Blueprint, render_template

bp = Blueprint("test", __name__, url_prefix="/test")


@bp.route("/exception")
async def raise_exception():
    raise Exception


@bp.route("/")
async def root(): ...


@bp.route("/dialog")
async def dialog():
    return await render_template("test/dialog.html")
