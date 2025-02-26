from quart import (
    Blueprint,
    current_app,
    g,
    redirect,
    render_template,
    request,
    flash,
    url_for,
    abort,
)
from quart_babel import _

from .. import api
from ..core.comments import postComment, postStamp, deleteComment
from ..core.illustManagement import getInternalIllustDetails
from ..core.user import getUserBookmarks, getNotifications
from ..core.artwork import getFrequentTags
from ..core.comments import getReplyAndRoot
from ..core.my_profile import getProfileConfig

from aiohttp import MultipartWriter
import json
from werkzeug.datastructures import FileStorage
import logging

log = logging.getLogger("pyxiv.routes.userAction")


userAction = Blueprint("userAction", __name__, url_prefix="/self")


@userAction.route("/")
async def redirectToSelf():

    return await redirect(f"/users/{g.userdata._id}")


@userAction.route("/bookmarks")
async def yourBookmarks():

    page = int(request.args.get("p", 1))

    data = await getUserBookmarks(g.userdata._id, offset=(48 * page) - 48, limit=48)
    frequent = await getFrequentTags([x._id for x in data.works])

    pages, extra = divmod(data.total, 48)

    if extra > 0:
        pages += 1

    return await render_template(
        "bookmarksSelf.html",
        data=data,
        pages=pages,
        frequent=frequent,
        canGoNext=(page < pages and not page == pages),
        canGoPrevious=(not page == 1),
    )


@userAction.route("/addbookmark/<int:_id>")
async def addBookmark(_id: int):

    await api.pixivReq(
        "post",
        "/ajax/illusts/bookmarks/add",
        jsonPayload={"illust_id": str(_id), "restrict": 0, "comment": "", "tags": []},
    )

    await flash(_("Successfully bookmarked post"))
    return redirect(request.args["r"])


@userAction.route("/removebookmark/<int:_id>")
async def deleteBookmark(_id: int):

    await api.pixivReq(
        "post", "/ajax/illusts/bookmarks/delete", rawPayload=f"bookmark_id={_id}"
    )

    await flash(_("Successfully removed bookmark"))
    return redirect(request.args["r"])


@userAction.route("/like/<int:_id>")
async def likeIllust(_id: int):

    await api.pixivReq(
        "post", "/ajax/illusts/like", jsonPayload={"illust_id": str(_id)}
    )

    await flash(_("Successfully liked post"))
    return redirect(request.args["r"])


@userAction.post("/comment")
async def comment():
    args = request.args
    form = await request.form
    try:
        await postComment(args["id"], args["author"], form["comment"])
    except Exception as e:
        log.exception("Unable to post comment")
        await flash(
            _(
                "Unable to post comment: %(errorClass)s: %(error)s",
                errorClass=e.__class__.__name__,
                error=str(e),
            ),
            "error",
        )
    else:
        await flash(_("Successfully posted comment"))

    return redirect(url_for("artworks.artworkComments", _id=args["id"]))


@userAction.post("/postStamp")
async def stamp():
    args = request.args
    form = await request.form
    try:
        await postStamp(args["id"], args["author"], form["stampId"])
    except Exception as e:
        log.exception("Unable to post stamp")
        await flash(
            _(
                "Unable to send stamp: %(errorClass)s: %(error)s",
                errorClass=e.__class__.__name__,
                error=str(e),
            ),
            "error",
        )
    else:
        await flash(_("Successfully sent stamp"))

    return redirect(url_for("artworks.artworkComments", _id=args["id"]))


@userAction.get("/delete_comment")
async def comment_delete():
    args = request.args

    illustId = args["i_id"]
    commentId = args["del_id"]

    try:
        await deleteComment(illustId, commentId)
        await flash(_("Successfully deleted comment"))
    except Exception as e:
        log.exception("Unable to delee comment")
        await flash(
            _(
                "Unable to delete comment: %(errorClass)s: %(error)s",
                errorClass=e.__class__.__name__,
                error=str(e),
            ),
            "error",
        )
    return redirect(url_for("artworks.artworkComments", _id=illustId))


@userAction.route("/notifications")
async def notifications():

    return await render_template("notifications.html", data=await getNotifications())


@userAction.post("/favorite_tags/save")
async def addTagToFavorites():
    await api.addTagToFavorites(request.form["tag"])
    return await redirect(request.args.get("r", "/"))


@userAction.route("/followUser/<int:_id>")
async def followUser(_id: int):
    restrict = bool(int(request.args.get("restrict", 0)))
    r = request.args.get("r", "/")

    if _id == g.userdata._id:
        await flash(_("You cannot follow yourself."), "error")
        return redirect(r, code=303)

    if _id == 0:
        await flash(_("Invalid user"), "error")
        return redirect(r, code=303)
    try:
        await api.followUser(_id, restrict)
    except api.PixivError:
        await flash(_("Could not follow user"), "error")
    else:
        await flash(_("Successfully followed user"))
    return redirect(r, code=303)


@userAction.route("/unfollowUser/<int:_id>")
async def unfollowUser(_id: int):
    r = request.args.get("r", "/")
    if _id == 0:
        await flash(_("Invalid user"), "error")
        return await redirect(r, code=303)
    try:
        await api.unfollowUser(_id)
    except api.PixivError:
        await flash(_("Could not unfollow user"), "error")
    else:
        await flash(_("Successfully unfollowed user"))
    return redirect(r, code=303)


@userAction.route("/reply_and_root")
async def replyAndRoot():
    if not request.args.get("illust_id") or not request.args.get("comment_id"):
        abort(400)

    child, root = await getReplyAndRoot(
        request.args.get("illust_id"), request.args.get("comment_id")
    )
    return await render_template("reply_and_root.html", child=child, root=root)


@userAction.route("/editIllustration/<int:id>", methods=["GET", "POST"])
async def editIllustration(id: int):
    if request.method == "POST":
        f = await request.form
        title = f["title"]
        caption = f["caption"]
        restrict = f["restrict"]
        xRestrict = f["xRestrict"]
        aiGenerated = f.get("aigc") == "on"
        allowComment = f.get("allowComment") == "on"
        allowTagEdit = f.get("allowTagEdit") == "on"
        original = f.get("original") == "on"

        await api.editIllustrationDetails(
            id,
            title=title,
            caption=caption,
            restrict=restrict,
            aiGenerated=aiGenerated,
            allowComment=allowComment,
            allowTagEdit=allowTagEdit,
            original=original,
            xRestrict=xRestrict,
        )

        await flash(_("Successfully edited details"))
        return redirect(f"/artworks/{id}", code=303)
    else:
        data = await getInternalIllustDetails(id)
        return await render_template("editDetails.html", data=data)


@userAction.route("/editProfile", methods=("GET", "POST"))
async def editProfile():
    if request.method == "POST":
        data = (await api.getMyProfile())["body"]
        f = await request.form
        files = await request.files

        mp = MultipartWriter("form-data")

        profile: FileStorage = files["profile_image"]
        cover: FileStorage = files["cover_image"]
        data["name"] = f["name"]
        data["comment"] = f.get("comment", "")
        data["coverImage"] = None
        data["profileImage"] = None

        pData = profile.read()
        coData = cover.read()

        if len(pData) > 0:
            log.debug("Adding and validating profile image")
            validationMp = MultipartWriter("form-data")
            valProfile = validationMp.append(
                pData, {"Content-Type": profile.content_type}
            )
            valProfile.set_content_disposition(
                "form-data", name="profile_image", filename=profile.name
            )
            await api.pixivReq(
                "post",
                "/ajax/my_profile/validate_profile_image",
                {"Referer": "https://www.pixiv.net/settings/profile"},
                rawPayload=validationMp,
            )
            log.debug("Successfully validated profile image")
            profileMp = mp.append(pData, {"Content-Type": profile.content_type})
            profileMp.set_content_disposition(
                "form-data", name="profile_image", filename=profile.name
            )
        if len(coData) > 0:
            log.debug("Adding cover image")
            coverMp = mp.append(coData, {"Content-Type": cover.content_type})
            coverMp.set_content_disposition(
                "form-data", name="cover_image", filename=cover.name
            )

        log.debug(json.dumps(data))
        profd = mp.append(json.dumps(data))
        profd.set_content_disposition("form-data", name="profile")
        log.debug("Finalizing...")
        await api.pixivReq(
            "post",
            "/ajax/my_profile/update",
            rawPayload=mp,
            additionalHeaders={
                "Referer": "https://www.pixiv.net/settings/profile"
            },
        )

        await flash(_("Your profile has been updated"))
        return redirect(url_for("users.userPage", _id=g.userdata._id), code=303)

    else:
        data = await getProfileConfig()
        return await render_template("edit_profile.html", data=data)
