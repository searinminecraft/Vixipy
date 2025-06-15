from quart import (
    Blueprint,
    redirect,
    render_template,
    url_for,
)

bp = Blueprint("settings", __name__)

@bp.route("/settings")
async def root():
    return ""