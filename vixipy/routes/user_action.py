from __future__ import annotations

from quart import Blueprint, make_response, request, redirect, url_for, g, abort

from ..api import pixiv_request
from typing import TYPE_CHECKING
from urllib.parse import quote
from quart_babel import lazy_gettext as _l

if TYPE_CHECKING:
    from typing import Union

bp = Blueprint("user_action", __name__)

HX_HEADER = '{"X-Vixipy-Quick-Action": "true"}'  #  work around for python


@bp.before_request
async def ensure_authorized():
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


@bp.post("/self/action/delete_bookmark/<int:id>")
async def delete_bookmark(id: int):
    f = await request.form
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    rt = f.get("return_to", "/")

    await pixiv_request(
        "/ajax/illusts/bookmarks/delete", "post", raw_payload=f"bookmark_id={id}"
    )

    if isQuickAction:
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
