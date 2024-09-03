from flask import Blueprint, render_template

from core.artwork import getArtwork, getArtworkPages, getRelatedArtworks
from core.user import getUser
from classes import ArtworkDetailsPage


artworks = Blueprint("artworks", __name__, url_prefix="/artworks")


@artworks.route("/<int:_id>")
def artworkGet(_id: int):

    artworkData = getArtwork(_id)
    pageData = getArtworkPages(_id)
    userData = getUser(artworkData.authorId)
    relatedData = getRelatedArtworks(_id)

    return render_template(
        "artwork.html",
        data=ArtworkDetailsPage(artworkData, pageData, userData, relatedData),
    )
