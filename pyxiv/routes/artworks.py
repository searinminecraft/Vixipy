from flask import Blueprint, render_template, request, flash, redirect, url_for

from ..core.artwork import getArtwork, getArtworkPages, getRelatedArtworks
from ..core.user import getUser
from ..core.comments import getArtworkComments
from ..classes import ArtworkDetailsPage


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


@artworks.route("/<int:_id>/comments")
def artworkComments(_id: int):

    artworkData = getArtwork(_id)

    if artworkData.commentOff:
        flash("The creator turned off comments.", "error")
        return redirect(url_for("artworks.artworkGet", _id=_id))

    data = getArtworkComments(_id, **request.args)

    return render_template(
        "comments.html", comments=data, illustId=_id, authorId=artworkData.authorId
    )
