from flask import Blueprint, render_template

from core.artwork import getArtwork, getArtworkPages
from classes import ArtworkDetailsPage


artworks = Blueprint("artworks", __name__, url_prefix="/artworks")

@artworks.route("/<int:_id>")
def artworkGet(_id: int):

    artworkData = getArtwork(_id)
    pageData = getArtworkPages(_id)

    return render_template("artwork.html", data=ArtworkDetailsPage(artworkData, pageData))
