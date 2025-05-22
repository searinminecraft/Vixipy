from quart import (
    Blueprint,
    render_template,
    request
)

from ..api import get_discovery

bp = Blueprint("discovery", __name__)

@bp.route("/discovery")
async def discovery_root():
    data = await get_discovery(
        mode=request.args.get("mode", "all")
    )

    return await render_template("discovery/illustrations.html", data=data)