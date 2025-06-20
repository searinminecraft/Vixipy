from quart import Blueprint, g, abort, redirect, render_template, request, url_for

from ..decorators import require_login

bp = Blueprint("upload", __name__)


@bp.route("/illustrations/upload")
@require_login
async def upload_main():
    if not g.authorized:
        return redirect(url_for("login.login_page", return_to="/illustrations/upload"))

    return await render_template("upload.html")


@bp.post("/self/illustration/upload")
async def do_upload():
    """This is gonna be spicy"""
    if not g.authorized:
        abort(403)

    f = await request.form
    files = await request.files

    print(request.files)
