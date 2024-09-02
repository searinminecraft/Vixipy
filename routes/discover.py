from flask import Blueprint, render_template

from core.discovery import getDiscoveryData

discover = Blueprint("discover", __name__, url_prefix="/discover")

@discover.route("/")
def discoverMain():

    data = getDiscoveryData("all", 50)

    return render_template("discover.html", data=data)
