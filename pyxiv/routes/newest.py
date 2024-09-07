from flask import Blueprint, render_template

from ..core.discovery import getNewestArtworks

newest = Blueprint("newest", __name__, url_prefix="/newest")

@newest.route("/")
def newestMain():

    data = getNewestArtworks()

    return render_template("newest.html", data=data)
