from flask import Blueprint, render_template, request

from ..core.discovery import getDiscoveryData

discover = Blueprint("discover", __name__, url_prefix="/discover")


@discover.route("/")
def discoverMain():

    mode = request.args.get("mode", "safe")

    if mode not in ("all", "safe", "r18"):
        raise ValueError(f"Invalid mode: {mode}")

    data = getDiscoveryData(mode, 50)

    return render_template("discover.html", data=data)
