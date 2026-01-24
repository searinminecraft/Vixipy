from quart import Blueprint, request, abort, render_template

bp = Blueprint("jump", __name__)


@bp.get("/jump.php")
async def main():
    try:
        if request.args.get("url"):
            # /jump.php?url=https://kita.codeberg.page
            dest = request.args["url"]
        else:
            # /jump.php?https://kita.codeberg.page
            dest = list(request.args.keys())[0]
    except (IndexError, KeyError):
        abort(400)

    return await render_template("leave.html.j2", url=dest)
