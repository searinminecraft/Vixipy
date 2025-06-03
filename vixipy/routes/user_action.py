from __future__ import annotations

from quart import (
    Blueprint,
    request,
    redirect,
    url_for,
    g,
    abort
)

from ..api import pixiv_request
from typing import TYPE_CHECKING
from quart_babel import lazy_gettext as _l

if TYPE_CHECKING:
    from typing import Union

bp = Blueprint("user_action", __name__)

HX_HEADER = '{"X-Vixipy-Quick-Action": "true"}' #  work around for python

@bp.before_request
async def ensure_authorized():
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    if not g.get("authorized"):
        if isQuickAction:
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
            headers={"Referer": f"https://www.pixiv.net/en/users/{id}", "Origin": "https://www.pixiv.net"}
        )
        if isQuickAction:
            return (
f"""
<form action="/self/action/user/{id}/unfollow"
    hx-push-url="false" hx-swap="outerHTML show:none" hx-target="this" hx-indicator="this"
    hx-headers='{HX_HEADER}' method="post">
    <input type="hidden" name="return_to" value="{rt}">
    <button type="submit" class="button neutral">
        {_l("Unfollow")}
    </button>
</form>
"""
            )
        else:
            return redirect(rt, code=303)
    elif action == "unfollow":
        await pixiv_request(
            "/touch/ajax_api/ajax_api.php",
            "post",
            raw_payload=f"mode=delete_bookmark_user&user_id={id}",
            headers={"Referer": f"https://www.pixiv.net/en/users/{id}", "Origin": "https://www.pixiv.net"}
        )
        if isQuickAction:
            return (
f"""
<form action="/self/action/user/{id}/follow"
    hx-push-url="false" hx-swap="outerHTML show:none" hx-target="this" hx-indicator="this"
    hx-headers='{HX_HEADER}' method="post">
    <input type="hidden" name="return_to" value="{rt}">
    <button type="submit" class="button primary">
        {_l("Follow")}
    </button>
</form>
"""
            )
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
                "tags": []
            }
        )

        if isQuickAction:
            return (
f"""
<form action="/self/action/delete_bookmark/{data['last_bookmark_id']}" method="post"
hx-swap="outerHTML show:none" hx-target="this" hx-push-url="false" hx-indicator="this"
hx-headers='{HX_HEADER}'>
    <input type="hidden" name="return_to" id="{request.path}">
    <input type="hidden" name="bookmark_count" value="{int(f["bookmark_count"]) + 1}">
    <input type="hidden" name="work_id" value="{id}">
    <button type="submit">
        <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e3e3e3"><path d="m480-170.93-36.15-32.69q-98.46-88.23-162.5-150.57-64.04-62.35-100.58-109.93-36.54-47.57-50.65-86.27Q116-589.08 116-629q0-80.15 55.42-135.58Q226.85-820 307-820q49.38 0 95 23.5t78 67.27q32.38-43.77 78-67.27 45.62-23.5 95-23.5 80.15 0 135.58 55.42Q844-709.15 844-629q0 39.92-13.62 77.61-13.61 37.7-50.15 84.77-36.54 47.08-100.89 110.43Q615-292.85 514.15-201.62L480-170.93Z"/></svg>
        {int(f["bookmark_count"]) + 1}
    </button>
</form>
"""
            )
        else:
            return redirect(rt, code=303)

    if action == "like":
        await pixiv_request(
            "/ajax/illusts/like",
            "post",
            json_payload={"illust_id": str(id)}
        )

        if isQuickAction:
            return (
f"""
<svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e3e3e3"><path d="M709.23-164H257.08v-440l273.38-271.84L546.3-870q17.24 12.23 25.35 30.5 8.12 18.27 3.12 37.35V-806L538.3-604h289.39q26.54 0 45.42 18.89Q892-566.23 892-539.69v41.61q0 7.23-1.31 12.96t-3.92 11.97L773.15-205.69q-8.61 19.23-25.84 30.46T709.23-164ZM205.08-604v440H68v-440h137.08Z"/></svg>
{int(f['like_count']) + 1}
"""
            )
        else:
            return redirect(rt, code=303)


@bp.post("/self/action/delete_bookmark/<int:id>")
async def delete_bookmark(id: int):
    f = await request.form
    isQuickAction = request.headers.get("X-Vixipy-Quick-Action") == "true"
    rt = f.get("return_to", "/")

    await pixiv_request(
        "/ajax/illusts/bookmarks/delete",
        "post",
        raw_payload=f"bookmark_id={id}"
    )

    if isQuickAction:
        return (
f"""
<form action="/self/action/works/{f['work_id']}/bookmark" method="post"
hx-swap="outerHTML show:none" hx-target="this" hx-push-url="false" hx-indicator="this"
hx-headers='{HX_HEADER}'>
    <input type="hidden" name="return_to" id="{request.path}">
    <input type="hidden" name="bookmark_count" value="{int(f["bookmark_count"]) - 1}">
    <input type="hidden" name="work_id" value="{f['work_id']}">
    <button type="submit">
        <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e8eaed"><path d="M479.62-194.62q-11.85 0-22.81-4.11-10.96-4.12-20.81-12.96l-47.46-43.23q-109.38-97-190.96-187.58Q116-533.08 116-634q0-79.17 54.27-132.58Q224.55-820 305-820q46.58 0 92.18 21.31 45.59 21.31 82.82 72.46 39.23-51.15 84.08-72.46Q608.94-820 654.68-820q80.47 0 134.9 53.42Q844-713.17 844-634q0 102.08-83.5 193.23-83.5 91.15-189.04 185.46l-47.85 43.62q-9.84 8.84-20.99 12.96-11.16 4.11-23 4.11Zm-24.39-475.84q-27.46-49.46-66.35-73.5Q350-768 305-768q-58.71 0-97.86 38Q168-692 168-633.61q0 46.76 30.04 96.8t75.42 100.46q45.38 50.43 98.58 97.96 53.19 47.54 99.88 89.08 3.46 3.08 8.08 3.08t8.08-3.08q46.69-41.54 99.88-89.08 53.2-47.53 98.58-97.96 45.38-50.42 75.42-100.46Q792-586.85 792-633.61 792-692 752.86-730q-39.15-38-97.86-38-45 0-84.38 24.04-39.39 24.04-66.85 73.5-3.08 7.69-9.82 11.04-6.74 3.34-14 3.34t-14.45-3.34q-7.19-3.35-10.27-11.04ZM480-506.54Z"/></svg>
        {int(f["bookmark_count"]) - 1}
    </button>
</form>
"""
            )
    else:
        return redirect(rt, code=303)