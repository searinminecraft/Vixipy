from quart import (
    Blueprint, g, redirect, render_template, url_for
)

bp = Blueprint("upload", __name__)

@bp.route("/illustrations/upload")
async def upload_main():
    if not g.authorized:
        return redirect(url_for("login.login_page", return_to="/illustrations/upload"))
    
    return await render_template("upload.html")