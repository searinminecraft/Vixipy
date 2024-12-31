from quart import Blueprint, render_template

devtest = Blueprint("devtest", __name__, url_prefix="/devtest")


@devtest.route("/error")
async def error():
    return 1 / 0


@devtest.route("/tmplerr")
async def tmplerr():
    return await render_template("devtest/tmplerr.html")
