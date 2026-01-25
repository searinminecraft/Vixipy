from __future__ import annotations

import random
import string
from asyncio import gather
from quart import flash, g, make_response, request, redirect, url_for
from quart_babel import _
from typing import TYPE_CHECKING

from .api.handler import PixivError
from .api.user import get_notification_count, get_self_extra, get_user

if TYPE_CHECKING:
    from quart import Quart
    from .types import User, UserExtraData


def _generate_ab_cookies() -> tuple[str, str, str, str]:
    """
    Generates yuid_b and three ab cookie values.
    """
    yuidb_chars = string.ascii_letters + string.digits
    yuidb_length = 7
    ab_id_upper_bound = 10

    yuidb = "".join(random.choices(yuidb_chars, k=yuidb_length))

    # Non-negative pseudo-random 31-bit integer.
    p_ab_d_id = str(random.randint(0, 2**31 - 1))

    p_ab_id = str(random.randint(0, ab_id_upper_bound - 1))
    p_ab_id_2 = str(random.randint(0, ab_id_upper_bound - 1))

    return yuidb, p_ab_d_id, p_ab_id, p_ab_id_2


async def get_session_data():
    if any(
        request.path.startswith(f"/{x}")
        for x in ("favicon.ico", "robots.txt", "static", "proxy", "sass", ".well-known")
    ):
        return

    c = request.cookies
    g.authorized = c.get("Vixipy-Token")
    g.language = c.get("Vixipy-Language")

    if g.authorized:
        g.token = c.get("Vixipy-Token")
        g.csrf = c.get("Vixipy-CSRF")
        g.p_ab_d_id = c.get("Vixipy-p_ab_d_id")
        g.p_ab_id = c.get("Vixipy-p_ab_id")
        g.p_ab_id_2 = c.get("Vixipy-p_ab_id_2")
        g.yuid_b = c.get("Vixipy-yuid_b")

        if (
            any([request.path.startswith("/" + x) for x in ("api", "_partials")])
            or request.headers.get("X-Vixipy-Quick-Action") == "true"
        ):
            return

        try:
            notification_count, user, extra = await gather(
                get_notification_count(),
                get_user(g.token.split("_")[0]),
                get_self_extra(),
            )
        except PixivError:
            r = await make_response(
                redirect(url_for("login.login_page", return_to=request.path), code=303)
            )
            r.delete_cookie("Vixipy-Token")
            r.delete_cookie("Vixipy-p_ab_id")
            r.delete_cookie("Vixipy-p_ab_id_2")
            r.delete_cookie("Vixipy-p_ab_d_id")
            r.delete_cookie("Vixipy-yuid_b")
            r.delete_cookie("Vixipy-CSRF")
            await flash(_("Session not valid. Please sign in."))
            return r

        notification_count: int
        user: User
        extra: UserExtraData

        g.current_user = user
        g.notification_count = notification_count
        g.current_user_extra = extra


def init_app(app: Quart):
    app.before_request(get_session_data)
