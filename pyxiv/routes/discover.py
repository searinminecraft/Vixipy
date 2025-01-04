from quart import Blueprint, render_template, request
from quart_rate_limiter import limit_blueprint, timedelta

from ..core.discovery import getDiscoveryData

discover = Blueprint("discover", __name__, url_prefix="/discover")
limit_blueprint(discover, 10, timedelta(seconds=30))


@discover.route("/")
async def discoverMain():

    mode = request.args.get("mode", "safe")

    if mode not in ("all", "safe", "r18"):
        raise ValueError(f"Invalid mode: {mode}")

    data = await getDiscoveryData(mode, 50)

    return await render_template("discover.html", data=data)
