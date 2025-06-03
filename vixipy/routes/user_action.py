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