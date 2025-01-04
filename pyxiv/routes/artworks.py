from quart import (
    Blueprint,
    abort,
    current_app,
    g,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from asyncio import gather
from quart_babel import _
from quart_rate_limiter import limit_blueprint, timedelta, RateLimit

from ..api import PixivError
from ..core.artwork import getArtwork, getArtworkPages, getRelatedArtworks
from ..core.user import getUser
from ..core.comments import getArtworkComments, getArtworkReplies
from ..classes import ArtworkDetailsPage


artworks = Blueprint("artworks", __name__, url_prefix="/artworks")
limit_blueprint(artworks, limits=[RateLimit(1, timedelta(seconds=3)), RateLimit(10, timedelta(minutes=1))])


@artworks.route("/<int:_id>")
async def artworkGet(_id: int):

    c = request.cookies

    artworkData = await getArtwork(_id)

    if current_app.config["nor18"] and artworkData.xRestrict >= 1:
        # mimic pixiv's behavior, which is to vaguely return
        # a 404 if the illust is R-18(G)
        abort(404)

    if request.cookies.get("VixipyHideSensitive") == "1" and artworkData.isSensitive:
        return (
            await render_template(
                "error.html",
                errortitle=_("You cannot access this illustration"),
                errordesc=_(
                    'This illustration is potentially sensitive. To view it, turn off the "Hide potentially sensitive content" setting.'
                ),
            ),
            400,
        )

    if request.cookies.get("PyXivHideAI") == "1" and artworkData.isAI:
        return (
            await render_template(
                "error.html",
                errortitle=_("You cannot access this illustration"),
                errordesc=_(
                    'This illustration is AI generated. To view it, turn off the "Hide AI generated works" setting.'
                ),
            ),
            400,
        )

    if request.cookies.get("PyXivHideR18") == "1" and artworkData.xRestrict >= 1:
        return (
            await render_template(
                "error.html",
                errortitle=_("You cannot access this illustration"),
                errordesc=_(
                    'This illustration is rated as R-18. To view it, turn off the "Hide explicit content (R-18)" setting.'
                ),
            ),
            400,
        )

    if request.cookies.get("PyXivHideR18G") == "1" and artworkData.xRestrict == 2:
        return (
            await render_template(
                "error.html",
                errortitle=_("You cannot access this illustration"),
                errordesc=_(
                    'This illustration is rated as R-18G. To view it, turn off the "Hide ero-guro (R-18G) content" setting.'
                ),
            ),
            400,
        )

    pageData, userData, relatedData = await gather(
        getArtworkPages(_id),
        getUser(artworkData.authorId),
        getRelatedArtworks(_id, 100),
    )

    return await render_template(
        "artwork.html",
        data=ArtworkDetailsPage(artworkData, pageData, userData, relatedData),
    )


@artworks.route("/<int:_id>/comments")
async def artworkComments(_id: int):

    artworkData, data = await gather(
        getArtwork(_id), getArtworkComments(_id, **request.args)
    )

    if artworkData.commentOff:
        await flash(_("The creator turned off comments."), "error")
        return await redirect(url_for("artworks.artworkGet", _id=_id))

    return await render_template(
        "comments.html", comments=data, illustId=_id, authorId=artworkData.authorId
    )


@artworks.route("/<int:_id>/comments/replies/<int:commentId>")
async def artworkReplies(_id: int, commentId: int):

    data = await getArtworkReplies(commentId)
    return await render_template(
        "replies.html", comments=data, illustId=_id, commentId=commentId
    )
