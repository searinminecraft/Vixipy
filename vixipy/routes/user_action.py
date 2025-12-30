from __future__ import annotations

from quart import Blueprint, make_response, request, redirect, url_for, g, abort

from ..api.handler import pixiv_request
from ..api.search import get_tag_info
from typing import TYPE_CHECKING
from urllib.parse import quote
from quart_babel import lazy_gettext as _l

if TYPE_CHECKING:
    from typing import Union

bp = Blueprint("user_action", __name__)

HX_HEADER = '{"X-Vixipy-Quick-Action": "true"}'  #  work around for python


@bp.before_request
async def ensure_authorized():
    if request.path == "/self/consent":
        return

    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    if not g.get("authorized"):
        if isQuickAction:
            abort(401)
        if request.method == "POST":
            abort(401)
        return redirect(url_for("login.login_page"))


@bp.post("/self/action/user/<int:id>/<action>")
async def follow_unfollow(id: int, action: Union["follow", "unfollow"]):
    f = await request.form
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    rt = f.get("return_to", "/")

    if action == "follow":
        await pixiv_request(
            "/touch/ajax_api/ajax_api.php",
            "post",
            raw_payload=f"mode=add_bookmark_user&restrict=0&user_id={id}",
            headers={
                "Referer": f"https://www.pixiv.net/en/users/{id}",
                "Origin": "https://www.pixiv.net",
            },
        )
        if isQuickAction:
            return f"""
<form action="/self/action/user/{id}/unfollow"
    hx-push-url="false" hx-swap="outerHTML show:none" hx-target="this" hx-indicator="this"
    hx-headers='{HX_HEADER}' method="post">
    <input type="hidden" name="return_to" value="{rt}">
    {"<input type='hidden' name='small'>" if 'small' in f else ''}
    <button type="submit" class="button {'smaller' if 'small' in f else ''} neutral">
        {_l("Following")}
    </button>
</form>
"""
        else:
            return redirect(rt, code=303)
    elif action == "unfollow":
        await pixiv_request(
            "/touch/ajax_api/ajax_api.php",
            "post",
            raw_payload=f"mode=delete_bookmark_user&user_id={id}",
            headers={
                "Referer": f"https://www.pixiv.net/en/users/{id}",
                "Origin": "https://www.pixiv.net",
            },
        )
        if isQuickAction:
            return f"""
<form action="/self/action/user/{id}/follow"
    hx-push-url="false" hx-swap="outerHTML show:none" hx-target="this" hx-indicator="this"
    hx-headers='{HX_HEADER}' method="post">
    <input type="hidden" name="return_to" value="{rt}">
    {"<input type='hidden' name='small'>" if 'small' in f else ''}
    <button type="submit" class="button {'smaller' if 'small' in f else ''} primary">
        {_l("Follow")}
    </button>
</form>
"""
        else:
            return redirect(rt, code=303)


@bp.post("/self/action/works/<int:id>/<action>")
async def perform_work_action(id: int, action: Union["bookmark", "like"]):
    f = await request.form
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    withinArtwork = f.get("within_illust")
    rt = f.get("return_to", "/")

    if action == "bookmark":
        data = await pixiv_request(
            "/ajax/illusts/bookmarks/add",
            "post",
            json_payload={
                "illust_id": str(id),
                "restrict": 0,
                "comment": "",
                "tags": [],
            },
        )

        if isQuickAction:

            if withinArtwork:
                return f"""
                <form action="/self/action/delete_bookmark/{data['last_bookmark_id']}" method="post"
                    hx-swap="outerHTML show:none" hx-target="this" hx-push-url="false"
                    hx-headers='{HX_HEADER}'>

                    <input type="hidden" name="return_to" id="{request.path}">
                    <input type="hidden" name="work_id" value="{id}">
                    <input type="hidden" name="within_illust" value="1">

                    <button type="submit" class="bookmarked">
                        <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M480-147q-14 0-28.5-5T426-168l-69-63q-106-97-191.5-192.5T80-634q0-94 63-157t157-63q53 0 100 22.5t80 61.5q33-39 80-61.5T660-854q94 0 157 63t63 157q0 115-85 211T602-230l-68 62q-11 11-25.5 16t-28.5 5Z"/></svg>
                    </button>
                </form>
                """

            return f"""
<form action="/self/action/delete_bookmark/{data['last_bookmark_id']}" method="post"
hx-swap="outerHTML show:none" hx-target="this" hx-push-url="false" hx-indicator="this"
hx-headers='{HX_HEADER}'>
    <input type="hidden" name="return_to" id="{request.path}">
    <input type="hidden" name="bookmark_count" value="{int(f["bookmark_count"]) + 1}">
    <input type="hidden" name="work_id" value="{id}">
    <button type="submit">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11 2H5a2 2 0 00-2 2v10l5-2.5 5 2.5V4a2 2 0 00-2-2z"/></svg>
        {int(f["bookmark_count"]) + 1}
    </button>
</form>
"""
        else:
            return redirect(rt, code=303)

    if action == "like":
        await pixiv_request(
            "/ajax/illusts/like", "post", json_payload={"illust_id": str(id)}
        )

        if isQuickAction:
            return f"""
<svg class="liked" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 8a2 2 0 100-4 2 2 0 000 4zM12 8a2 2 0 100-4 2 2 0 000 4zM11.89 10.89a5.5 5.5 0 01-7.78 0 1 1 0 011.415-1.415 3.5 3.5 0 004.95 0 1 1 0 111.414 1.414z"/></svg>
{int(f['like_count']) + 1}
"""
        else:
            return redirect(rt, code=303)


@bp.post("/self/action/remove_favorite_tag")
async def remove_favorite_tag():
    f = await request.form
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    rt = f.get("return_to", "/")
    tag = f.get("tag")

    if not tag:
        abort(400)

    tag_info = await get_tag_info(tag)
    if not tag_info.is_favorite:
        abort(400)

    tag_info.favorite_tags.remove(tag)

    await pixiv_request(
        "/ajax/favorite_tags/save",
        "post",
        json_payload={"tags": tag_info.favorite_tags},
    )

    if isQuickAction:
        return f"""
        <form id="favorites-action" action="/self/action/add_favorite_tag" method="post" hx-push-url="false"
                hx-swap="outerHTML show:none" hx-target="this" hx-headers='{HX_HEADER}'>

                <input type="hidden" name="tag" value="{tag}">
                <input type="hidden" name="return_to" value="{rt}">

                <button type="submit" class="button primary">{_l("Add to your favorites")}</button>
        </form>
        """


@bp.post("/self/action/add_favorite_tag")
async def add_favorite_tag():
    f = await request.form
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    rt = f.get("return_to", "/")
    tag = f.get("tag")

    if not tag:
        abort(400)

    tag_info = await get_tag_info(tag)
    if tag_info.is_favorite:
        abort(400)

    tag_info.favorite_tags.append(tag)

    await pixiv_request(
        "/ajax/favorite_tags/save",
        "post",
        json_payload={"tags": tag_info.favorite_tags},
    )

    if isQuickAction:
        return f"""
        <form id="favorites-action" action="/self/action/remove_favorite_tag" method="post" hx-push-url="false"
                hx-swap="outerHTML show:none" hx-target="this" hx-headers='{HX_HEADER}'>

                <input type="hidden" name="tag" value="{tag}">
                <input type="hidden" name="return_to" value="{rt}">

                <button type="submit" class="button neutral">{_l("Remove from favorites")}</button>
        </form>
        """


@bp.post("/self/action/delete_bookmark/<int:id>")
async def delete_bookmark(id: int):
    f = await request.form
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    withinArtwork = f.get("within_illust")
    rt = f.get("return_to", "/")

    await pixiv_request(
        "/ajax/illusts/bookmarks/delete", "post", raw_payload=f"bookmark_id={id}"
    )

    if isQuickAction:
        if withinArtwork:
            return f"""
                <form action="/self/action/works/{f['work_id']}/bookmark" method="post"
                    hx-swap="outerHTML show:none" hx-target="this" hx-push-url="false"
                    hx-headers='{HX_HEADER}'>

                    <input type="hidden" name="return_to" id="{request.path}">
                    <input type="hidden" name="work_id" value="{f['work_id']}">
                    <input type="hidden" name="within_illust" value="1">


                    <button type="submit">
                        <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M480-147q-14 0-28.5-5T426-168l-69-63q-106-97-191.5-192.5T80-634q0-94 63-157t157-63q53 0 100 22.5t80 61.5q33-39 80-61.5T660-854q94 0 157 63t63 157q0 115-85 211T602-230l-68 62q-11 11-25.5 16t-28.5 5Zm-38-543q-29-41-62-62.5T300-774q-60 0-100 40t-40 100q0 52 37 110.5T285.5-410q51.5 55 106 103t88.5 79q34-31 88.5-79t106-103Q726-465 763-523.5T800-634q0-60-40-100t-100-40q-47 0-80 21.5T518-690q-7 10-17 15t-21 5q-11 0-21-5t-17-15Zm38 189Z"/></svg>
                    </button>
                </form>
                """

        return f"""
<form action="/self/action/works/{f['work_id']}/bookmark" method="post"
hx-swap="outerHTML show:none" hx-target="this" hx-push-url="false" hx-indicator="this"
hx-headers='{HX_HEADER}'>
    <input type="hidden" name="return_to" id="{request.path}">
    <input type="hidden" name="bookmark_count" value="{int(f["bookmark_count"]) - 1}">
    <input type="hidden" name="work_id" value="{f['work_id']}">
    <button type="submit">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M8 11.5l5 2.5V4a2 2 0 00-2-2H5a2 2 0 00-2 2v10l5-2.5zm-4 .882l4-2 4 2V4a1 1 0 00-1-1H5a1 1 0 00-1 1v8.382z"/></svg>
        {int(f["bookmark_count"]) - 1}
    </button>
</form>
"""
    else:
        return redirect(rt, code=303)


@bp.post("/self/post_comment")
async def post_comment():
    f = await request.form

    illust_id: str = f["target"]
    user: str = f["user"]
    comment: str = f["comment"]

    # Validate for pixiv restrictions
    if len(comment) > 140:
        abort(400)
    if comment.rstrip() == "":
        abort(400)

    await pixiv_request(
        "/rpc/post_comment.php",
        "post",
        raw_payload=f"type=comment&illust_id={illust_id}&author_user_id={user}&comment={quote(comment)}",
        headers={
            "Accept": "application/json",
            "Origin": "https://www.pixiv.net",
            "Referer": "https://www.pixiv.net/artworks/" + illust_id,
        },
    )

    return redirect(url_for("artworks.get_comments", id=int(illust_id)))


@bp.post("/self/post_stamp")
async def post_stamp():
    f = await request.form

    illust_id: str = f["target"]
    user: str = f["user"]
    stamp: str = f["id"]

    await pixiv_request(
        "/rpc/post_comment.php",
        "post",
        raw_payload=f"type=stamp&illust_id={illust_id}&author_user_id={user}&stamp_id={stamp}",
        headers={
            "Accept": "application/json",
            "Origin": "https://www.pixiv.net",
            "Referer": "https://www.pixiv.net/artworks/" + illust_id,
        },
    )

    return redirect(url_for("artworks.get_comments", id=int(illust_id)))


@bp.get("/self/logout")
async def logout():
    r = await make_response(redirect("/"))
    r.delete_cookie("Vixipy-Token")
    r.delete_cookie("Vixipy-p_ab_id")
    r.delete_cookie("Vixipy-p_ab_id_2")
    r.delete_cookie("Vixipy-p_ab_d_id")
    r.delete_cookie("Vixipy-yuid_b")
    r.delete_cookie("Vixipy-CSRF")
    return r


@bp.get("/self/consent")
async def consent():
    r = await make_response(redirect(request.args.get("r", "/")))
    r.set_cookie("Vixipy-Consented", "1", httponly=True)
    return r
