from quart import (
    Blueprint,
    render_template
)

bp = Blueprint("index", __name__)

@bp.get("/")
async def index():
    return await render_template("index.html")